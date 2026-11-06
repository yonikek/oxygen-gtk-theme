#!/usr/bin/env python3
"""Generate the symbolic glyphs shipped in src/assets.

The shapes are taken from the KDE Oxygen style (kstyle/oxygenstyle.cpp:
renderTitleBarIcon, genericArrow, renderCheckBox, renderRadioButton): polylines
drawn with round caps and joins. GTK recolours symbolic SVGs by *filling*
paths, so every stroke is converted to filled capsules (rotated rounded
rectangles), which union into the original stroke.

Each glyph has two layers, like Oxygen draws them:
  * a contrast copy, offset downwards, with class="warning" (the stylesheet
    maps this to a light colour derived from the surface behind the glyph)
  * the main glyph, which GTK recolours with the widget's foreground colour
"""
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "src", "assets")


def capsule(p, q, w):
    (x1, y1), (x2, y2) = p, q
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 1e-6:
        return '<circle cx="%.3f" cy="%.3f" r="%.3f"/>' % (x1, y1, w / 2)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return ('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f" '
            'transform="rotate(%.3f %.3f %.3f)"/>'
            % (mx - length / 2 - w / 2, my - w / 2, length + w, w, w / 2,
               ang, mx, my))


def polyline(points, w, closed=False):
    pts = list(points) + ([points[0]] if closed else [])
    return "".join(capsule(a, b, w) for a, b in zip(pts, pts[1:]))


def shift(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def svg(size, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">\n%s</svg>\n' % (size, size, size, size, body))


def layered(size, shapes, w, dy, closed=False):
    """shapes: list of point lists. Contrast copy first, then the main glyph."""
    contrast = "".join(polyline(shift(s, 0, dy), w, closed) for s in shapes)
    main = "".join(polyline(shift(s, 0, -dy), w, closed) for s in shapes)
    return svg(size, '<g class="warning">%s</g>\n<g>%s</g>\n' % (contrast, main))


glyphs = {}

# --- window controls: 16x16 grid, pen 1.1, contrast +-0.5 -------------------
W = 1.1
glyphs["oxygen-close-symbolic.svg"] = layered(
    16, [[(5.5, 5.5), (10.5, 10.5)], [(10.5, 5.5), (5.5, 10.5)]], W, 0.5)
glyphs["oxygen-minimize-symbolic.svg"] = layered(
    16, [[(5, 7), (8, 10), (11, 7)]], W, 0.5)
glyphs["oxygen-maximize-symbolic.svg"] = layered(
    16, [[(5, 9), (8, 6), (11, 9)]], W, 0.5)
glyphs["oxygen-maximized-symbolic.svg"] = layered(
    16, [[(8, 5), (11, 8), (8, 11), (5, 8)]], W, 0.5, closed=True)

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
        16, "<g>%s</g>\n" % polyline(arrow(pts), 1.6))

# --- check mark (pen 2) and radio bullet (r 2.6) on a 14x14 box -------------
CHECK = [(12, 5), (6, 12), (3, 9)]
glyphs["checkmark-symbolic.svg"] = layered(14, [CHECK], 2.0, 0.5)
glyphs["bullet-symbolic.svg"] = svg(
    14,
    '<g class="warning"><circle cx="7" cy="7.65" r="2.6"/></g>\n'
    '<g><circle cx="7" cy="6.35" r="2.6"/></g>\n')

# --- window control ring (StyleHelper::dockWidgetButton) --------------------
# Oxygen strokes a circle (diameter 12.33 on an 18 grid, pen 1.2) with a
# gradient that is dark at the top and light at the bottom. Recolouring only
# fills flat colours, so the gradient is approximated by a dark ring (class
# "success") over the lower half of a light ring (class "warning") that sits
# slightly lower. The stylesheet picks both colours from the titlebar colour.
CX, CY, R_OUT, R_IN = 9.0, 8.27, 6.165, 4.965


def annulus(cx, cy, ro, ri):
    return ('<path fill-rule="evenodd" d="M %.3f %.3f A %.3f %.3f 0 1 0 %.3f %.3f '
            'A %.3f %.3f 0 1 0 %.3f %.3f Z M %.3f %.3f A %.3f %.3f 0 1 1 %.3f %.3f '
            'A %.3f %.3f 0 1 1 %.3f %.3f Z"/>'
            % (cx - ro, cy, ro, ro, cx + ro, cy, ro, ro, cx - ro, cy,
               cx - ri, cy, ri, ri, cx + ri, cy, ri, ri, cx - ri, cy))


def lower_half_annulus(cx, cy, ro, ri):
    return ('<path d="M %.3f %.3f A %.3f %.3f 0 0 0 %.3f %.3f L %.3f %.3f '
            'A %.3f %.3f 0 0 1 %.3f %.3f Z"/>'
            % (cx - ro, cy, ro, ro, cx + ro, cy, cx + ri, cy,
               ri, ri, cx - ri, cy))


glyphs["oxygen-wc-ring-symbolic.svg"] = svg(
    18,
    '<g class="warning">%s</g>\n<g class="success">%s</g>\n'
    % (lower_half_annulus(CX, CY + 0.9, R_OUT, R_IN),
       annulus(CX, CY - 0.1, R_OUT, R_IN)))

for fname, content in glyphs.items():
    with open(os.path.join(OUT, fname), "w") as fh:
        fh.write(content)
print("wrote", len(glyphs), "glyphs")
