"""Site icons from each site's glyph (the same one its card shows in "More courses"): favicon.svg, favicon-32.png, apple-touch-icon.png.
The glyph is turned into an SVG path (fonttools), so the icon does not depend on fonts on the phone.
Usage: python3 tools/icons.py   (needs: pip install fonttools; ImageMagick for the PNGs)"""
import os, subprocess
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

NOTO = '/usr/share/fonts/truetype/noto/'
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
SITES = {  # folder: (glyph, font, background, glyph colour)
    'ThaiFast': ('ก', 'NotoSansThai-Bold.ttf', '#e8b04b', '#09090b'),
    'EngFast': ('Aa', 'NotoSans-Bold.ttf', '#e8b04b', '#09090b'),
    'SumerFast': ('𒀭', 'NotoSansCuneiform-Regular.ttf', '#e8b04b', '#09090b'),
    'BrainFast': ('Ψ', 'NotoSans-Bold.ttf', '#e8b04b', '#09090b'),
}

def glyph_path(text, font, box):
    """SVG path of text, scaled to fit a box×box square and centred in a 32×32 viewBox"""
    f = TTFont(NOTO + font); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    names = [cmap[ord(c)] for c in text]
    # lay the glyphs out on one baseline, then measure the ink
    bp, x = BoundsPen(gs), 0
    for n in names:
        gs[n].draw(TransformPen(bp, (1, 0, 0, 1, x, 0))); x += gs[n].width
    x0, y0, x1, y1 = bp.bounds
    k = box / max(x1 - x0, y1 - y0)
    dx, dy = 16 - (x0 + x1) / 2 * k, 16 + (y0 + y1) / 2 * k   # y is flipped
    sp, x = SVGPathPen(gs), 0
    for n in names:
        gs[n].draw(TransformPen(sp, (k, 0, 0, -k, dx + x * k, dy))); x += gs[n].width
    return sp.getCommands()

for site, (text, font, bg, fg) in SITES.items():
    d = os.path.join(DOCS, site)
    path = glyph_path(text, font, 19 if len(text) > 1 else 18)
    svg = lambda rx: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="{rx}" fill="{bg}"/><path d="{path}" fill="{fg}"/></svg>\n'
    open(os.path.join(d, 'favicon.svg'), 'w').write(svg(8))
    tmp = os.path.join(d, '.touch.svg'); open(tmp, 'w').write(svg(0))   # iOS/Android round the corners themselves
    subprocess.run(['convert', '-background', 'none', '-density', '384', os.path.join(d, 'favicon.svg'), '-resize', '32x32', os.path.join(d, 'favicon-32.png')], check=True)
    subprocess.run(['convert', '-density', '1600', tmp, '-resize', '180x180', os.path.join(d, 'apple-touch-icon.png')], check=True)
    os.remove(tmp)
    print(site, 'icons written')
