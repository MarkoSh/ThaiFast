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
# lucide icons (ISC licence) drawn as strokes, for sites without a fitting letter
LUCIDE = {
    'brain': ['M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z', 'M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z',
              'M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4', 'M17.599 6.5a3 3 0 0 0 .399-1.375', 'M6.003 5.125A3 3 0 0 0 6.401 6.5', 'M3.477 10.896a4 4 0 0 1 .585-.396',
              'M19.938 10.5a4 4 0 0 1 .585.396', 'M6 18a4 4 0 0 1-1.967-.516', 'M19.967 17.484A4 4 0 0 1 18 18'],
}
SITES = {  # folder: (glyph, font, background, glyph colour); font 'lucide' = glyph is a LUCIDE name
    'ThaiFast': ('ก', 'NotoSansThai-Bold.ttf', '#e8b04b', '#09090b'),
    'EngFast': ('Aa', 'NotoSans-Bold.ttf', '#e8b04b', '#09090b'),
    'SumerFast': ('𒀭', 'NotoSansCuneiform-Regular.ttf', '#e8b04b', '#09090b'),
    'BrainFast': ('brain', 'lucide', '#e8b04b', '#09090b'),
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
    if font == 'lucide':   # 24-unit icon scaled to 22 px, as on the page
        art = f'<g transform="translate(5 5) scale(.9167)" fill="none" stroke="{fg}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + ''.join(f'<path d="{d}"/>' for d in LUCIDE[text]) + '</g>'
    else:
        art = f'<path d="{glyph_path(text, font, 19 if len(text) > 1 else 18)}" fill="{fg}"/>'
    svg = lambda rx: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="{rx}" fill="{bg}"/>{art}</svg>\n'
    open(os.path.join(d, 'favicon.svg'), 'w').write(svg(8))
    tmp = os.path.join(d, '.touch.svg'); open(tmp, 'w').write(svg(0))   # iOS/Android round the corners themselves
    subprocess.run(['convert', '-background', 'none', '-density', '384', os.path.join(d, 'favicon.svg'), '-resize', '32x32', os.path.join(d, 'favicon-32.png')], check=True)
    subprocess.run(['convert', '-density', '1600', tmp, '-resize', '180x180', os.path.join(d, 'apple-touch-icon.png')], check=True)
    os.remove(tmp)
    print(site, 'icons written')
