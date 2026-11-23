"""The Word version of a pack (participant or mentor, see pack_spec.py).

Same content file as the PDF, so the two cannot say different things. Arial throughout, on
purpose: a .docx only carries font NAMES, and a name that is not installed on the reader's
machine is silently swapped for something else and the page re-flows.

The banner sits in the header, full bleed. Three things make that work in Word: header
distance 0, negative indents equal to the page margins, and an inline picture as wide as
the sheet.
"""
import pathlib
import re
import sys

from docx import Document
from docx.enum.table import (WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE,
                             WD_TABLE_ALIGNMENT)
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Mm, Pt, RGBColor

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / 'output' / 'documents'
sys.path.insert(0, str(HERE))
from pack_spec import BLOCKS, MAILBOX, SITE, SPEC, day_foot    # noqa: E402

NAME = SPEC['name']
FONT = 'Arial'
INK, PAPER, ACCENT, BRAND = '121316', 'F2F1E9', '7E98FF', '141A9D'
BODY, SLATE, RULE = '23252B', '5D6068', 'DCDAD0'

MARGIN_MM = 20
TEXT_MM = 210 - 2 * MARGIN_MM          # 170


# ------------------------------------------------------------------ xml bits
# WordprocessingML is a sequence schema: the children of pPr, rPr, tcPr, tblPr
# and trPr must appear in one fixed order. Word forgives some misorderings and
# reports others as "unreadable content", and it does not say which is which.
# So nothing here is appended blindly — put() places every element where the
# schema wants it.
ORDER = {
    'tcPr': ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap',
             'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark'],
    'tblPr': ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
              'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders',
              'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption', 'tblDescription'],
    'trPr': ['cnfStyle', 'divId', 'gridBefore', 'gridAfter', 'wBefore', 'wAfter', 'cantSplit',
             'trHeight', 'tblHeader', 'tblCellSpacing', 'jc', 'hidden'],
    'pPr': ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
            'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
            'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE',
            'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
            'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
            'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
            'sectPr', 'pPrChange'],
    'rPr': ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
            'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
            'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs',
            'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
            'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'],
}


def _local(el):
    return el.tag.rsplit('}', 1)[-1]


def put(parent, child):
    """Insert child into parent at the position the schema requires."""
    order = ORDER[_local(parent)]
    later = set(order[order.index(_local(child)) + 1:])
    for el in parent:
        if _local(el) in later:
            el.addprevious(child)
            return child
    parent.append(child)
    return child


def _el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn('w:' + k), str(v))
    return e


def force_font(rpr, name=FONT):
    """Set the face and strip the theme pointers that would override it."""
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = put(rpr, OxmlElement('w:rFonts'))
    for a in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        if rf.get(qn('w:' + a)) is not None:
            del rf.attrib[qn('w:' + a)]
    for a in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        rf.set(qn('w:' + a), name)


def colour(run_or_font, hexcode):
    font = getattr(run_or_font, 'font', run_or_font)
    font.color.rgb = RGBColor.from_string(hexcode)
    c = font._element.rPr.find(qn('w:color'))
    for a in ('themeColor', 'themeTint', 'themeShade'):
        if c is not None and c.get(qn('w:' + a)) is not None:
            del c.attrib[qn('w:' + a)]


def track(run, points):
    """Letter-spacing, in points."""
    put(run._element.get_or_add_rPr(), _el('w:spacing', val=int(points * 20)))


def shade(cell, fill):
    put(cell._tc.get_or_add_tcPr(), _el('w:shd', val='clear', color='auto', fill=fill))


def borders(cell, **edges):
    """edges: top=(size_eighths, colour) ..."""
    b = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):       # itself a sequence
        if edge in edges:
            size, col = edges[edge]
            b.append(_el('w:' + edge, val='single', sz=size, space=0, color=col))
    put(cell._tc.get_or_add_tcPr(), b)


def padding(cell, top=0, left=0, bottom=0, right=0):
    """Cell padding in millimetres."""
    mar = OxmlElement('w:tcMar')
    for edge, mm in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        mar.append(_el('w:' + edge, w=int(mm * 56.7), type='dxa'))
    put(cell._tc.get_or_add_tcPr(), mar)


def para_border(par, edge, size, gap_pt, hexcode):
    bdr = OxmlElement('w:pBdr')
    bdr.append(_el('w:' + edge, val='single', sz=size, space=gap_pt, color=hexcode))
    put(par._p.get_or_add_pPr(), bdr)


def new_table(doc, rows, widths_mm):
    """A borderless fixed-width table whose edge sits exactly on the margin."""
    t = doc.add_table(rows=rows, cols=len(widths_mm))
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    tblpr = t._tbl.tblPr
    put(tblpr, _el('w:tblInd', w=0, type='dxa'))
    mar = OxmlElement('w:tblCellMar')
    for edge in ('top', 'left', 'bottom', 'right'):
        mar.append(_el('w:' + edge, w=0, type='dxa'))
    put(tblpr, mar)
    for i, w in enumerate(widths_mm):
        t.columns[i].width = Mm(w)
        for cell in t.columns[i].cells:
            cell.width = Mm(w)
    return t


def keep_row_whole(row):
    put(row._tr.get_or_add_trPr(), _el('w:cantSplit'))


def field(par, instr, size, hexcode):
    """A live Word field, e.g. PAGE or NUMPAGES."""
    for kind, text in (('begin', None), (None, instr), ('separate', None), ('text', '1'), ('end', None)):
        run = par.add_run()
        run.font.size = Pt(size)
        colour(run, hexcode)
        if kind in ('begin', 'separate', 'end'):
            run._element.append(_el('w:fldChar', fldCharType=kind))
        elif kind == 'text':
            run.text = text
        else:
            it = OxmlElement('w:instrText')
            it.set(qn('xml:space'), 'preserve')
            it.text = f' {instr} '
            run._element.append(it)


# ------------------------------------------------------------------- writing
def write(par, text, size=None, hexcode=None, bold=False):
    """Add text to a paragraph, turning **x** into bold runs."""
    for i, chunk in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        if not chunk:
            continue
        run = par.add_run(chunk)
        run.bold = True if (bold or i % 2) else None
        if size:
            run.font.size = Pt(size)
        if hexcode:
            colour(run, hexcode)
    return par


def space(par, before=0, after=0, line=None, keep=False):
    f = par.paragraph_format
    f.space_before, f.space_after = Pt(before), Pt(after)
    if line:
        f.line_spacing = line
    if keep:
        f.keep_with_next = True
    return par


def eyebrow(par, text, hexcode=BRAND, size=7.5, spacing=1.4):
    run = par.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    colour(run, hexcode)
    track(run, spacing)
    return par


def build_docx(banner_first, banner_next):
    from make_pack import photo_strip, TITLE
    doc = Document()

    # ------------------------------------------------------------ page setup
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = Mm(MARGIN_MM)
    sec.top_margin, sec.bottom_margin = Mm(20), Mm(19)
    sec.header_distance, sec.footer_distance = Mm(0), Mm(8)
    sec.different_first_page_header_footer = True

    # ---------------------------------------------------------------- styles
    normal = doc.styles['Normal']
    normal.font.name, normal.font.size = FONT, Pt(10)
    force_font(normal.element.get_or_add_rPr())
    colour(normal.font, BODY)
    put(normal.element.get_or_add_rPr(), _el('w:lang', val='en-GB'))
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.18

    h1 = doc.styles['Heading 1']
    h1.font.name, h1.font.size, h1.font.bold = FONT, Pt(13.5), True
    force_font(h1.element.get_or_add_rPr())
    colour(h1.font, BRAND)
    h1.paragraph_format.space_before, h1.paragraph_format.space_after = Pt(15), Pt(4)
    h1.paragraph_format.keep_with_next = True

    for name in ('List Bullet', 'List Number', 'Header', 'Footer'):
        force_font(doc.styles[name].element.get_or_add_rPr())

    # ------------------------------------------------------- header + footer
    def banner(header, png, alt):
        header.is_linked_to_previous = False
        p = header.paragraphs[0]
        f = p.paragraph_format
        f.left_indent, f.right_indent = -sec.left_margin, -sec.right_margin
        f.space_before, f.space_after = Pt(0), Pt(15)
        f.line_spacing = 1.0
        run = p.add_run()
        run.font.size = Pt(1)
        pic = run.add_picture(str(png), width=sec.page_width)
        pic._inline.docPr.set('descr', alt)
        pic._inline.docPr.set('title', 'Header banner')

    alt = ('Example College, Example College of Business and Technology. AI Entrepreneurship Hackathon. '
           f"{''.join(SPEC['banner']).title()}. 23 to 26 October 2026, Example Campus. Powered by Example Campus.")
    banner(sec.first_page_header, banner_first, alt)
    banner(sec.header, banner_next, alt)

    def foot(footer):
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0]
        # The built-in Footer style carries a centre tab at 4680 and a right tab
        # at 9360. Clearing the paragraph's own tabs does not remove those, and
        # the tab character lands on the first one it meets — which centred
        # "Page 1 of 5" in the middle of the line. They have to be cancelled
        # explicitly, each at its own position.
        tabs = p.paragraph_format.tab_stops
        tabs.add_tab_stop(Emu(4680 * 635), WD_TAB_ALIGNMENT.CLEAR)
        tabs.add_tab_stop(Emu(9360 * 635), WD_TAB_ALIGNMENT.CLEAR)
        tabs.add_tab_stop(Mm(TEXT_MM), WD_TAB_ALIGNMENT.RIGHT)
        para_border(p, 'top', 4, 6, RULE)
        write(p, f'{MAILBOX}   ·   {SITE}\tPage ', 7.5, SLATE)
        field(p, 'PAGE', 7.5, SLATE)
        write(p, ' of ', 7.5, SLATE)
        field(p, 'NUMPAGES', 7.5, SLATE)

    foot(sec.first_page_footer)
    foot(sec.footer)

    # ------------------------------------------------------------------ body
    break_next = False

    def para(text='', size=None, hexcode=None, style=None):
        nonlocal break_next
        p = doc.add_paragraph(style=style)
        if text:
            write(p, text, size, hexcode)
        if break_next:
            p.paragraph_format.page_break_before = True
            break_next = False
        return p

    def gap(points):
        """A fixed sliver of space after a table, where Word gives none."""
        p = doc.add_paragraph()
        space(p, 0, 0, line=Pt(points))
        return p

    for blk in BLOCKS:
        kind = blk[0]

        if kind == 'pagebreak':
            break_next = True

        elif kind == 'eyebrow':
            space(eyebrow(para(), blk[1], spacing=1.8), 0, 5)

        elif kind == 'lead':
            space(para(blk[1], 12, INK), 0, 6, line=1.25)

        elif kind == 'p':
            para(blk[1])

        elif kind == 'small':
            space(para(blk[1], 8.5, SLATE), 4, 4)

        elif kind == 'h':
            p = para(style='Heading 1')
            p.add_run(blk[1])

        elif kind == 'glance':
            rows = blk[2]
            t = new_table(doc, len(rows) + 1, [36, TEXT_MM - 36])
            head = t.rows[0].cells[0].merge(t.rows[0].cells[1])
            shade(head, PAPER)
            padding(head, top=3.2, left=4, bottom=0.6, right=4)
            space(eyebrow(head.paragraphs[0], blk[1]), 0, 2)
            for i, (label, value) in enumerate(rows, start=1):
                a, b = t.rows[i].cells
                last = i == len(rows)
                for cell in (a, b):
                    shade(cell, PAPER)
                    if not last:
                        borders(cell, bottom=(4, RULE))
                padding(a, top=1.5, left=4, bottom=1.5 if not last else 3, right=2)
                padding(b, top=1.5, left=0, bottom=1.5 if not last else 3, right=4)
                space(write(a.paragraphs[0], label, 7.5, BRAND, bold=True), 1.2, 0)
                space(write(b.paragraphs[0], value, 9.5), 0, 0, line=1.15)
                keep_row_whole(t.rows[i])
            gap(4)

        elif kind == 'checks':
            for item in blk[1]:
                space(para(item, 9.5, style='List Number'), 0, 3)

        elif kind == 'bullets':
            for item in blk[1]:
                space(para(item, 9.5, style='List Bullet'), 0, 3)

        elif kind == 'days':
            card, gutter = 83, 4
            t = new_table(doc, 3, [card, gutter, card])
            t.rows[1].height = Pt(8)
            t.rows[1].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in t.rows[1].cells:
                space(cell.paragraphs[0], 0, 0, line=Pt(2))
            for r, c, d in ((0, 0, blk[1][0]), (0, 2, blk[1][1]), (2, 0, blk[1][2]), (2, 2, blk[1][3])):
                cell = t.rows[r].cells[c]
                shade(cell, PAPER)
                borders(cell, top=(18, BRAND))
                padding(cell, top=3, left=3.5, bottom=3, right=3.5)
                space(eyebrow(cell.paragraphs[0], d['label']), 0, 2)
                space(write(cell.add_paragraph(), d['tagline'], 12, INK, bold=True), 0, 1)
                space(write(cell.add_paragraph(), f"{d['place']}  ·  {d['hours']}", 8, BODY, bold=True), 0, 5)
                for when, what in d['items']:
                    p = cell.add_paragraph()
                    f = p.paragraph_format
                    f.left_indent, f.first_line_indent = Mm(11.5), Mm(-11.5)
                    f.tab_stops.add_tab_stop(Mm(11.5))
                    write(p, when, 8.5, BRAND, bold=True)
                    p.add_run('\t')
                    write(p, what, 9)
                    space(p, 0, 2, line=1.1)
                p = cell.add_paragraph()
                write(p, day_foot(d)[0] + '  ', 7.5, BRAND, bold=True)
                write(p, day_foot(d)[1], 8.5, SLATE)
                space(p, 4, 0, line=1.1)
            for row in t.rows:
                keep_row_whole(row)
            gap(2)

        elif kind == 'quote':
            p = para(blk[1], 11, INK)
            p.paragraph_format.left_indent = Mm(4)
            para_border(p, 'left', 18, 8, ACCENT)
            space(p, 2, 8)

        elif kind in ('judging', 'pairs'):
            first = 16 if kind == 'judging' else 40
            t = new_table(doc, len(blk[1]), [first, TEXT_MM - first])
            for i, (label, value) in enumerate(blk[1]):
                a, b = t.rows[i].cells
                for cell in (a, b):
                    if i < len(blk[1]) - 1:
                        borders(cell, bottom=(4, RULE))
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                padding(a, top=1.6, bottom=1.6, right=2)
                padding(b, top=1.6, bottom=1.6)
                if kind == 'judging':
                    space(write(a.paragraphs[0], label, 14, BRAND, bold=True), 0, 0, line=1.0)
                    space(write(b.paragraphs[0], value, 9.5), 2.5, 0, line=1.15)
                else:
                    space(write(a.paragraphs[0], label, 7.5, BRAND, bold=True), 1.2, 0)
                    space(write(b.paragraphs[0], value, 9.5), 0, 0, line=1.15)
                keep_row_whole(t.rows[i])
            gap(7)

        elif kind == 'faq':
            for q, a in blk[1]:
                space(para(q, 10, INK), 0, 1.5, keep=True).runs[0].bold = True
                space(para(a, 9.5), 0, 8)

        elif kind == 'photos':
            strip = photo_strip(blk[1], TEXT_MM / 25.4 * 72)
            mm = [w / 72 * 25.4 for _, w, _ in strip]
            gutter = 6 / 72 * 25.4
            t = new_table(doc, 1, [w + (gutter if i < len(mm) - 1 else 0) for i, w in enumerate(mm)])
            alts = ('Example Campus, the brick building seen from the street', 'A shared work floor at Example Campus',
                    'A team room at Example Campus', 'The wooden staircase at Example Campus')
            for cell, (path, _, _), w, alt in zip(t.rows[0].cells, strip, mm, alts):
                p = cell.paragraphs[0]
                space(p, 0, 0, line=1.0)
                pic = p.add_run().add_picture(str(path), width=Mm(w))
                pic._inline.docPr.set('descr', alt)
            space(para(blk[2], 8.5, SLATE), 4, 6)

        elif kind == 'closing':
            d = blk[1]
            t = new_table(doc, 1, [104, TEXT_MM - 104])
            a, b = t.rows[0].cells
            for cell in (a, b):
                shade(cell, INK)
                # Two shaded cells side by side show a hairline of paper between
                # them when Word exports to PDF. Borders in the fill colour cover it.
                borders(cell, top=(4, INK), left=(4, INK), bottom=(4, INK), right=(4, INK))
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            padding(a, top=5, left=6, bottom=5, right=3)
            padding(b, top=5, left=0, bottom=5, right=6)
            space(eyebrow(a.paragraphs[0], d['eyebrow'], hexcode=ACCENT), 0, 3)
            space(write(a.add_paragraph(), d['title'], 14, PAPER, bold=True), 0, 3)
            space(write(a.add_paragraph(), d['text'], 9, 'D9D8D0'), 0, 0)
            p = b.paragraphs[0]
            write(p, f"**{d['name']}**, {d['role']}", 9, PAPER)
            lines = [p, write(b.add_paragraph(), d['lines'][0], 9, ACCENT),
                     write(b.add_paragraph(), d['lines'][1], 9, PAPER)]
            for ln in lines:
                ln.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                space(ln, 0, 1.5)
            keep_row_whole(t.rows[0])

        else:
            raise ValueError(kind)

    # python-docx's blank template ships <w:zoom w:val="bestFit"/> without the
    # percent attribute the schema requires. Word shrugs; a validator does not.
    zoom = doc.settings.element.find(qn('w:zoom'))
    if zoom is not None:
        zoom.set(qn('w:percent'), '100')

    # The template declares compatibilityMode 14 (Word 2010). In that mode a
    # table's indent is measured to the TEXT in its first cell, so every shaded
    # card slid left of the margin by its own padding. Mode 15 measures to the
    # cell edge, which is what the layout assumes — and it stops Word putting
    # "[Compatibility Mode]" in the title bar.
    for cs in doc.settings.element.iter(qn('w:compatSetting')):
        if cs.get(qn('w:name')) == 'compatibilityMode':
            cs.set(qn('w:val'), '15')

    cp = doc.core_properties
    cp.title, cp.author = TITLE, 'Example College'
    cp.subject = SPEC['subject']
    cp.keywords = SPEC['keywords']

    path = OUT / f'{NAME}.docx'
    doc.save(path)
    return path
