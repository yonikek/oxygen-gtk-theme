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

Gradients cannot survive recolouring, so they are built from translucent
overlays instead: a dark base shape, and n light copies of the upper part of it
with fill-opacity 1/(n-k+1), which composes to an exactly linear gradient.
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
SLAB_C = (10.5, 9.94)       # glossy slab: diameter 12.33 on an 18 grid
SLAB_R = 7.19
RING_C = (10.5, 10.34)      # outline circle, pen 0.7 on the same grid
RING_RO, RING_RI = 7.19, 6.37


def disc(cx, cy, r, cls=None, opacity=None):
    return '<circle cx="%.3f" cy="%.3f" r="%.3f"%s/>' % (cx, cy, r, attrs(cls, opacity))


def top_segment(cx, cy, r, y):
    """Path data for the part of a circle above the horizontal line y."""
    d = y - cy
    if d >= r - 1e-6:
        return None  # whole circle, caller uses a circle element
    if d <= -r + 1e-6:
        return ""    # empty
    a = math.sqrt(r * r - d * d)
    large = 1 if y > cy else 0
    return "M %.3f %.3f L %.3f %.3f A %.3f %.3f 0 %d 0 %.3f %.3f Z" % (
        cx - a, y, cx + a, y, r, r, large, cx - a, y)


def overlays(cx, cy, r_out, r_in, n, cls):
    """n light overlays over the upper part of a disc (r_in=None) or ring."""
    top, height = cy - r_out, 2 * r_out
    out = ""
    for j in range(1, n + 1):
        y = top + height * (n - j + 1) / n
        alpha = 1.0 / (n - j + 1)
        outer = top_segment(cx, cy, r_out, y)
        if r_in is None:
            if outer is None:
                out += disc(cx, cy, r_out, cls, alpha)
            elif outer:
                out += '<path%s d="%s"/>' % (attrs(cls, alpha), outer)
        else:
            outer_d = outer if outer is not None else (
                "M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f Z" % (
                    cx - r_out, cy, r_out, r_out, cx + r_out, cy, r_out, r_out, cx - r_out, cy))
            inner = top_segment(cx, cy, r_in, y)
            inner_d = inner if inner is not None else (
                "M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f Z" % (
                    cx - r_in, cy, r_in, r_in, cx + r_in, cy, r_in, r_in, cx - r_in, cy))
            if outer_d:
                out += '<path fill-rule="evenodd"%s d="%s %s"/>' % (
                    attrs(cls, alpha), outer_d, inner_d or "")
    return out


# slab file: shadow (error), dark base disc (success), light overlays (warning)
shadow = "".join(disc(10.5, 11.1, r, "error", a) for r, a in
                 ((9.4, 0.06), (8.8, 0.08), (8.2, 0.10), (7.6, 0.12)))
slab = (shadow + disc(*SLAB_C, SLAB_R, "success") +
        overlays(SLAB_C[0], SLAB_C[1], SLAB_R, None, 8, "warning"))
glyphs["oxygen-wc-slab-symbolic.svg"] = svg(21, slab + "\n")

# ring file: mid-tone ring (error) under light overlays on its upper part (warning)
ring_base = ('<path fill-rule="evenodd" class="error" d="'
             'M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f Z '
             'M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f Z"/>'
             % (RING_C[0] - RING_RO, RING_C[1], RING_RO, RING_RO, RING_C[0] + RING_RO, RING_C[1],
                RING_RO, RING_RO, RING_C[0] - RING_RO, RING_C[1],
                RING_C[0] - RING_RI, RING_C[1], RING_RI, RING_RI, RING_C[0] + RING_RI, RING_C[1],
                RING_RI, RING_RI, RING_C[0] - RING_RI, RING_C[1]))
glyphs["oxygen-wc-ring-symbolic.svg"] = svg(
    21, ring_base + overlays(RING_C[0], RING_C[1], RING_RO, RING_RI, 6, "warning") + "\n")


def annulus(cx, cy, ro, ri, opacity):
    return ('<path fill-rule="evenodd"%s d="M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f '
            'A %.3f %.3f 0 1 0 %.3f %.3f Z M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f '
            'A %.3f %.3f 0 1 0 %.3f %.3f Z"/>'
            % (attrs(None, opacity), cx - ro, cy, ro, ro, cx + ro, cy, ro, ro, cx - ro, cy,
               cx - ri, cy, ri, ri, cx + ri, cy, ri, ri, cx - ri, cy))


# glow file (hover): drawOuterGlow, a 3 unit wide halo fading outwards. It has
# no colour class, so it takes the widget's `color` (hover / negative colour).
glow = "".join(annulus(10.5, 10.3, ro, ri, a) for ro, ri, a in
               ((8.2, 7.2, 0.75), (9.2, 8.2, 0.40), (10.2, 9.2, 0.15)))
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
