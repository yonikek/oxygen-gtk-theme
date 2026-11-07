#!/usr/bin/env python3
"""Generate the symbolic glyphs shipped in src/assets.

Shapes and proportions come from the KDE Oxygen sources:
  * kstyle/oxygenstyle.cpp        arrows, check mark, radio dot
  * kdecoration/oxygenbutton.cpp  window control glyphs (21 unit grid, pen 1.2,
                                  light contrast copy 1.5 below the glyph)
  * kdecoration/oxygendecohelper.cpp  windecoButton(): shadow, glossy slab and
                                  outline of the window control buttons

GTK recolours symbolic SVGs by *filling* shapes. It does that through CSS rules
that match `rect`, `circle` and `path` directly, so the colour classes
(warning, success, error) must be on the shapes themselves, not on a wrapping
<g>. Strokes are converted to filled capsules (rotated rounded rectangles).

Gradients cannot survive recolouring, so they are built from bands of opaque
colours that the stylesheet chooses (see the oxy-titlebutton mixin).
"""
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "src", "assets")


def attrs(cls=None, opacity=None):
    out = ""
    if cls:
        out += ' class="%s"' % cls
    if opacity is not None and opacity < 1:
        out += ' fill-opacity="%.4f"' % opacity
    return out


def capsule(p, q, w, cls=None):
    (x1, y1), (x2, y2) = p, q
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 1e-6:
        return '<circle cx="%.3f" cy="%.3f" r="%.3f"%s/>' % (x1, y1, w / 2, attrs(cls))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return ('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f"%s '
            'transform="rotate(%.3f %.3f %.3f)"/>'
            % (mx - length / 2 - w / 2, my - w / 2, length + w, w, w / 2,
               attrs(cls), ang, mx, my))


def polyline(points, w, cls=None, closed=False):
    pts = list(points) + ([points[0]] if closed else [])
    return "".join(capsule(a, b, w, cls) for a, b in zip(pts, pts[1:]))


def shift(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def svg(size, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">\n%s</svg>\n' % (size, size, size, size, body))


def layered(size, shapes, w, contrast_dy, main_dy=0.0, closed=False):
    """Contrast copy first (class warning), then the main glyph (foreground)."""
    contrast = "".join(polyline(shift(s, 0, contrast_dy), w, "warning", closed)
                       for s in shapes)
    main = "".join(polyline(shift(s, 0, main_dy), w, None, closed) for s in shapes)
    return svg(size, contrast + "\n" + main + "\n")


glyphs = {}

# --- window control glyphs: 21 unit grid, pen 1.2, contrast copy 1.5 below ---
W = 1.2
glyphs["oxygen-close-symbolic.svg"] = layered(
    21, [[(7.5, 7.5), (13.5, 13.5)], [(13.5, 7.5), (7.5, 13.5)]], W, 1.5)
glyphs["oxygen-minimize-symbolic.svg"] = layered(
    21, [[(7.5, 9.5), (10.5, 12.5), (13.5, 9.5)]], W, 1.5)
glyphs["oxygen-maximize-symbolic.svg"] = layered(
    21, [[(7.5, 11.5), (10.5, 8.5), (13.5, 11.5)]], W, 1.5)
glyphs["oxygen-maximized-symbolic.svg"] = layered(
    21, [[(7.5, 10.5), (10.5, 7.5), (13.5, 10.5), (10.5, 13.5)]], W, 1.5,
    closed=True)

# --- window control button (DecoHelper::windecoButton), 21 unit grid --------
# Built only from opaque shapes, plain polygons and the four recolour classes:
# no fill-opacity, no fill-rule and no arc commands, so every SVG renderer GTK
# may use (librsvg or GTK's own) draws it the same way. Gradients are bands of
# opaque colours chosen in the stylesheet, which can mix them with the titlebar
# colour; transparency effects (shadow, glow) are mixed the same way.
SLAB_C = (10.5, 9.94)       # glossy slab: diameter 12.33 on an 18 grid
SLAB_R = 7.19
RING_C = (10.5, 10.34)      # outline circle, pen 0.7 on the same grid
RING_RO, RING_RI = 7.19, 6.37
SHADOW_C = (10.5, 11.1)
GLOW_C = (10.5, 10.3)
N = 48                      # polygon resolution of a full circle


def f(v):
    return "%.3f" % v


def disc(cx, cy, r, cls=None):
    return '<circle cx="%s" cy="%s" r="%s"%s/>' % (f(cx), f(cy), f(r), attrs(cls))


def poly_path(points, cls=None):
    d = "M " + " L ".join("%s %s" % (f(x), f(y)) for x, y in points) + " Z"
    return '<path%s d="%s"/>' % (attrs(cls), d)


def multi_path(polys, cls=None):
    d = " ".join("M " + " L ".join("%s %s" % (f(x), f(y)) for x, y in poly) + " Z"
                 for poly in polys)
    return '<path%s d="%s"/>' % (attrs(cls), d)


def circle_poly(cx, cy, r):
    """Counter-clockwise (on screen) polygon of a full circle."""
    return [(cx + r * math.cos(-2 * math.pi * i / N),
             cy + r * math.sin(-2 * math.pi * i / N)) for i in range(N)]


def top_poly(cx, cy, r, y):
    """Counter-clockwise polygon of the part of a circle above the line y."""
    d = y - cy
    if d >= r - 1e-6:
        return circle_poly(cx, cy, r)
    if d <= -r + 1e-6:
        return None
    alpha = math.asin(d / r)
    a = r * math.cos(alpha)
    pts = [(cx - a, y), (cx + a, y)]
    steps = max(4, int(N * (math.pi + 2 * alpha) / (2 * math.pi)))
    for i in range(1, steps + 1):
        phi = alpha - (math.pi + 2 * alpha) * i / steps
        pts.append((cx + r * math.cos(phi), cy + r * math.sin(phi)))
    return pts[:-1]  # the last point repeats the chord's left end


def disc_shape(cx, cy, r, y, cls):
    poly = top_poly(cx, cy, r, y)
    return "" if poly is None else poly_path(poly, cls)


def ring_shape(cx, cy, ro, ri, y, cls):
    """Annulus (hole wound the opposite way) restricted to the part above y."""
    outer = top_poly(cx, cy, ro, y)
    if outer is None:
        return ""
    inner = top_poly(cx, cy, ri, y)
    polys = [outer] + ([inner[::-1]] if inner else [])
    return multi_path(polys, cls)


def band_ys(cy, r, n):
    """Chord positions of n horizontal bands of a circle, lowest chord first."""
    top, height = cy - r, 2 * r
    return [top + height * (n - k) / n for k in range(1, n)]


# slab: nine bands, bottom to top, three recolour classes per file. File A holds
# the base disc and the two lowest bands; B and C hold the next three each (a
# file listed above another is drawn on top of it).
ys = band_ys(SLAB_C[1], SLAB_R, 9)
CLS = ("error", "warning", "success")
slab = [disc_shape(*SLAB_C, SLAB_R, 1e9, "error")]
slab += [disc_shape(*SLAB_C, SLAB_R, y, CLS[(i + 1) % 3]) for i, y in enumerate(ys)]
for name, chunk in (("a", slab[0:3]), ("b", slab[3:6]), ("c", slab[6:9])):
    glyphs["oxygen-wc-slab-%s-symbolic.svg" % name] = svg(21, "".join(chunk) + "\n")

# outline ring: a mid-tone ring whose upper part is lighter, in two steps
rtop, rh = RING_C[1] - RING_RO, 2 * RING_RO
ring = (ring_shape(*RING_C, RING_RO, RING_RI, 1e9, "error") +
        ring_shape(*RING_C, RING_RO, RING_RI, rtop + 0.65 * rh, "warning") +
        ring_shape(*RING_C, RING_RO, RING_RI, rtop + 0.35 * rh, "success"))
glyphs["oxygen-wc-ring-symbolic.svg"] = svg(21, ring + "\n")

# soft shadow below the slab: three discs fading outwards (drawn under it)
shadow = (disc_shape(*SHADOW_C, 9.4, 1e9, "error") +
          disc_shape(*SHADOW_C, 8.6, 1e9, "warning") +
          disc_shape(*SHADOW_C, 7.9, 1e9, "success"))
glyphs["oxygen-wc-shadow-symbolic.svg"] = svg(21, shadow + "\n")

# hover halo (drawOuterGlow): three rings around the slab fading outwards
glow = (ring_shape(*GLOW_C, 8.2, 7.2, 1e9, "error") +
        ring_shape(*GLOW_C, 9.2, 8.2, 1e9, "warning") +
        ring_shape(*GLOW_C, 10.2, 9.2, 1e9, "success"))
glyphs["oxygen-wc-glow-symbolic.svg"] = svg(21, glow + "\n")

# --- arrows: ArrowNormal, pen 1.6, centred in a 16x16 box -------------------
def arrow(pts):
    return [(8 + x, 8 + y) for x, y in pts]

ARROWS = {
    "up":    [(-3.5, 2), (0, -2), (3.5, 2)],
    "down":  [(-3.5, -2), (0, 2), (3.5, -2)],
    "left":  [(2, -3.5), (-2, 0), (2, 3.5)],
    "right": [(-2, -3.5), (2, 0), (-2, 3.5)],
}
for name, pts in ARROWS.items():
    glyphs["oxygen-arrow-%s-symbolic.svg" % name] = svg(
        16, polyline(arrow(pts), 1.6) + "\n")

# --- check mark (pen 2) and radio bullet (r 2.6) on a 14x14 box -------------
CHECK = [(12, 5), (6, 12), (3, 9)]
glyphs["checkmark-symbolic.svg"] = layered(14, [CHECK], 2.0, 0.5, -0.5)
glyphs["bullet-symbolic.svg"] = svg(
    14,
    disc(7, 7.65, 2.6, "warning") + "\n" + disc(7, 6.35, 2.6) + "\n")

for fname, content in glyphs.items():
    with open(os.path.join(OUT, fname), "w") as fh:
        fh.write(content)
print("wrote", len(glyphs), "glyphs")
