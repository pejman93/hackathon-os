"""Small helpers on top of python-pptx: measured text, real text boxes, tables, pictures and QR codes.
"""
import copy
import pathlib

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = pathlib.Path(__file__).resolve().parent
PROJ = HERE.parent
FONTS = PROJ / 'brand' / 'fonts'
(PROJ / 'output' / 'documents').mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = 595.276, 841.890            # A4 in points
SLIDE_W, SLIDE_H = 7559675, 10691813         # the Overview's own EMU values

INK, PAPER, ACCENT, BRAND = '121316', 'F2F1E9', '7E98FF', '141A9D'
BODY, SLATE, RULE, HAZE = '23252B', '5D6068', 'DCDAD0', 'B9BAC4'

DM, BC = 'DM Sans', 'Barlow Condensed'
DOT_COLOR = ACCENT          # colour of round bullets; a document may set another before it builds

# ------------------------------------------------------------------ measuring
_cloud = pathlib.Path.home() / 'Library/Group Containers/UBF8T346G9.Office/FontCache/4/CloudFonts'


def _register():
    reg = {('DM', False): FONTS / 'DMSans-400.ttf', ('DM', True): FONTS / 'DMSans-700.ttf',
           ('BC', True): FONTS / 'BarlowCondensed-700.ttf',
           # the repo has no Barlow Condensed Regular; SemiBold is a little wider,
           # so measuring with it can only over-estimate, which is the safe side
           ('BC', False): FONTS / 'BarlowCondensed-600.ttf'}
    for (fam, bold), path in reg.items():
        pdfmetrics.registerFont(TTFont(f'K{fam}{int(bold)}', str(path)))


_register()


def _key(font, bold):
    return f"K{'BC' if font == BC else 'DM'}{int(bool(bold))}"


class Run:
    def __init__(self, text, size=9.8, bold=False, color=BODY, font=DM, spc=0, link=None):
        self.text, self.size, self.bold, self.color, self.font, self.spc = text, size, bold, color, font, spc
        self.link = link                      # a URL or mailto: address; needs the slide's part to be written

    def width(self, s):
        return pdfmetrics.stringWidth(s, _key(self.font, self.bold), self.size) + self.spc * len(s)


class Para:
    """One paragraph. line = exact line pitch in points."""

    def __init__(self, runs, line=None, after=0, before=0, align='l', marL=0, indent=0,
                 tabs=(), bullet=None):
        self.runs = runs if isinstance(runs, (list, tuple)) else [runs]
        size = max(r.size for r in self.runs)
        self.line = line or round(size * 1.42, 1)
        self.after, self.before, self.align = after, before, align
        self.marL, self.indent, self.tabs, self.bullet = marL, indent, tuple(tabs), bullet

    def n_lines(self, width):
        """Greedy word wrap across runs of different faces."""
        avail = (width - self.marL) * 0.985          # a hair of slack against rounding
        tokens = []
        for r in self.runs:
            text = r.text.split('\t')[-1] if '\t' in r.text else r.text
            for i, word in enumerate(text.split(' ')):
                if i:
                    tokens.append((' ', r))
                if word:
                    tokens.append((word, r))
        lines, cur = 1, 0.0
        for tok, r in tokens:
            w = r.width(tok)
            if tok == ' ':
                cur += w
                continue
            if cur + w > avail and cur > 0:
                lines += 1
                cur = w
            else:
                cur += w
        return lines

    def height(self, width):
        return self.before + self.n_lines(width) * self.line + self.after


def height(paras, width):
    """Height of a stack of paragraphs; the last one's trailing space is dropped."""
    return sum(p.height(width) for p in paras) - (paras[-1].after if paras else 0)


def md(text, size=9.8, color=BODY, bold_color=None, font=DM, spc=0, link_color=BRAND):
    """'plain **bold** plain [words](https://...)' -> runs. A link may sit inside bold."""
    import re
    out = []
    for i, chunk in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        bold = bool(i % 2)
        for j, part in enumerate(re.split(r'(\[[^\]]+\]\([^)]+\))', chunk)):
            if not part:
                continue
            m = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', part) if j % 2 else None
            if m:
                out.append(Run(m.group(1), size, bold=bold, color=link_color, font=font, spc=spc, link=m.group(2)))
            else:
                out.append(Run(part, size, bold=bold, color=(bold_color or color) if bold else color,
                               font=font, spc=spc))
    return out


# ------------------------------------------------------------------- xml text
def _sub(parent, tag, **attrs):
    el = etree.SubElement(parent, qn(tag))
    for k, v in attrs.items():
        el.set(k, str(v))
    return el


def _para_xml(p, part=None):
    P = etree.Element(qn('a:p'))
    ppr = _sub(P, 'a:pPr', marL=int(p.marL * 12700), indent=int(p.indent * 12700))
    if p.align != 'l':
        ppr.set('algn', p.align)
    # children of a:pPr are a sequence: lnSpc, spcBef, spcAft, bu*, tabLst
    _sub(_sub(ppr, 'a:lnSpc'), 'a:spcPts', val=int(round(p.line * 100)))
    if p.before:
        _sub(_sub(ppr, 'a:spcBef'), 'a:spcPts', val=int(round(p.before * 100)))
    if p.after:
        _sub(_sub(ppr, 'a:spcAft'), 'a:spcPts', val=int(round(p.after * 100)))
    if p.bullet == 'num':
        _sub(_sub(ppr, 'a:buClr'), 'a:srgbClr', val=BRAND)
        _sub(ppr, 'a:buFont', typeface=DM)
        _sub(ppr, 'a:buAutoNum', type='arabicPeriod')
    elif p.bullet == 'box':                      # an empty tick-box; U+25A1 is in Arial on every machine
        _sub(_sub(ppr, 'a:buClr'), 'a:srgbClr', val=BRAND)
        _sub(ppr, 'a:buSzPct', val=130000)
        _sub(ppr, 'a:buFont', typeface='Arial')
        _sub(ppr, 'a:buChar', char='□')
    elif p.bullet == 'dot':
        _sub(_sub(ppr, 'a:buClr'), 'a:srgbClr', val=DOT_COLOR)
        _sub(ppr, 'a:buFont', typeface='Arial')
        _sub(ppr, 'a:buChar', char='•')
    else:
        _sub(ppr, 'a:buNone')
    if p.tabs:
        lst = _sub(ppr, 'a:tabLst')
        for t in p.tabs:
            _sub(lst, 'a:tab', pos=int(t * 12700), algn='l')
    for r in p.runs:
        R = _sub(P, 'a:r')
        rpr = _sub(R, 'a:rPr', lang='en-GB', sz=int(round(r.size * 100)), dirty='0')
        if r.bold:
            rpr.set('b', '1')
        if r.spc:
            rpr.set('spc', str(int(round(r.spc * 100))))
        _sub(_sub(rpr, 'a:solidFill'), 'a:srgbClr', val=r.color)
        _sub(rpr, 'a:latin', typeface=r.font)
        _sub(rpr, 'a:ea', typeface=r.font)
        _sub(rpr, 'a:cs', typeface=r.font)
        if getattr(r, 'link', None) and part is not None:        # a:hlinkClick comes after the typefaces
            rid = part.relate_to(r.link, RT.HYPERLINK, is_external=True)
            _sub(rpr, 'a:hlinkClick').set(qn('r:id'), rid)
        t = _sub(R, 'a:t')
        t.text = r.text
    _sub(P, 'a:endParaRPr', lang='en-GB', sz=int(round(p.runs[-1].size * 100)), dirty='0')
    return P


def _fill_body(txbody, paras, part=None):
    for old in txbody.findall(qn('a:p')):
        txbody.remove(old)
    for p in paras:
        txbody.append(_para_xml(p, part))


# ------------------------------------------------------------------ primitives
def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(SLIDE_W), Emu(SLIDE_H)
    return prs


def brand_links(prs, color=BRAND):
    """PowerPoint colours every hyperlink with the THEME's link colour, whatever the run
    says. So the theme is told to use the college blue (and the same once followed)."""
    import re
    theme = prs.slide_master.part.part_related_by(RT.THEME)
    xml = theme.blob.decode('utf-8')
    for tag in ('hlink', 'folHlink'):
        xml, n = re.subn(rf'(<a:{tag}>\s*<a:srgbClr val=")[0-9A-Fa-f]{{6}}(")', rf'\g<1>{color}\g<2>', xml)
        assert n == 1, f'theme has no <a:{tag}> to recolour'
    theme._blob = xml.encode('utf-8')


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])            # Blank


def text(slide, x, y, w, h, paras, name, anchor='t'):
    paras = paras if isinstance(paras, (list, tuple)) else [paras]
    tb = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'ctr': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    _fill_body(tb._element.txBody, paras, slide.part)
    return tb


def _plain(shape):
    """Drop the <p:style> python-pptx attaches. It points at the theme's effect
    and line styles, which is how a 0.6pt hairline came out as a soft grey band:
    the theme was adding a shadow to it."""
    st = shape._element.find(qn('p:style'))
    if st is not None:
        shape._element.remove(st)
    return shape


def rect(slide, x, y, w, h, fill, name, radius=0):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
    sh.name = name
    if radius:
        sh.adjustments[0] = min(0.5, radius / min(w, h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False                       # the theme would add one
    return _plain(sh)


def line(slide, x1, y1, x2, y2, color, name, width=0.6, alpha=None):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
    ln.name = name
    ln.line.color.rgb = RGBColor.from_string(color)
    ln.line.width = Pt(width)
    if alpha is not None:
        clr = ln.line._ln.find(qn('a:solidFill')).find(qn('a:srgbClr'))
        _sub(clr, 'a:alpha', val=int(alpha * 100000))
    return _plain(ln)


def picture(slide, path, x, y, w, h, name, alt):
    pic = slide.shapes.add_picture(str(path), Pt(x), Pt(y), Pt(w), Pt(h))
    pic.name = name
    pic._element.nvPicPr.cNvPr.set('descr', alt)
    return pic


NO_STYLE_NO_GRID = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'


def table(slide, x, y, widths, rows, name, fill=None, rule=RULE, pad=(4.3, 0, 4.5, 8), no_rule=(),
          outer=None, head_rule=None):
    """rows: list of rows; each row a list of cells; each cell a list of Para.
    pad = (top, left, bottom, right) in points. Returns (shape, total_height).
    A native table, so a row grows by itself when someone adds a line to it."""
    pads = pad if isinstance(pad[0], (tuple, list)) else [pad] * len(widths)   # one per column
    heights = []
    for row in rows:
        h = 0
        for cell, w, pd in zip(row, widths, pads):
            if cell:
                h = max(h, height(cell, w - pd[1] - pd[3]) + pd[0] + pd[2])
        heights.append(h)
    gf = slide.shapes.add_table(len(rows), len(widths), Pt(x), Pt(y), Pt(sum(widths)), Pt(sum(heights)))
    gf.name = name
    tbl = gf.table
    tbl.first_row = tbl.horz_banding = False
    gf._element.graphic.graphicData.tbl.tblPr.find(qn('a:tableStyleId')).text = NO_STYLE_NO_GRID
    for i, w in enumerate(widths):
        tbl.columns[i].width = Pt(w)
    for r, (row, h) in enumerate(zip(rows, heights)):
        tbl.rows[r].height = Pt(h)
        for c, paras in enumerate(row):
            cell = tbl.cell(r, c)
            pd = pads[c]
            cell.margin_top, cell.margin_left = Pt(pd[0]), Pt(pd[1])
            cell.margin_bottom, cell.margin_right = Pt(pd[2]), Pt(pd[3])
            cell.vertical_anchor = MSO_ANCHOR.TOP
            if fill:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor.from_string(fill)
            else:
                cell.fill.background()
            _fill_body(cell._tc.txBody, paras or [Para(Run(''))], slide.part)
            # a:tcPr is a sequence too: the four borders come before the fill
            tcpr = cell._tc.get_or_add_tcPr()
            last = r == len(rows) - 1
            for j, edge in enumerate(('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB')):
                ln = etree.Element(qn(edge))
                # outer = a box round the whole table; head_rule = a firmer line under row 1
                on_edge = outer and ((edge == 'a:lnL' and c == 0) or (edge == 'a:lnR' and c == len(row) - 1)
                                     or (edge == 'a:lnT' and r == 0) or (edge == 'a:lnB' and last))
                if on_edge:
                    ln.set('w', '9525')
                    _sub(_sub(ln, 'a:solidFill'), 'a:srgbClr', val=outer)
                elif edge == 'a:lnB' and head_rule and r == 0 and not last:
                    ln.set('w', '9525')
                    _sub(_sub(ln, 'a:solidFill'), 'a:srgbClr', val=head_rule)
                elif edge == 'a:lnB' and rule and not last and r not in no_rule:
                    ln.set('w', '6350')
                    _sub(_sub(ln, 'a:solidFill'), 'a:srgbClr', val=rule)
                else:
                    ln.set('w', '0')
                    _sub(ln, 'a:noFill')
                tcpr.insert(j, ln)
    return gf, sum(heights)


def qr_png(url, path, scale=24):
    import segno
    segno.make(url, error='h').save(str(path), scale=scale, border=2, dark='#' + INK, light='#ffffff')
    return path
