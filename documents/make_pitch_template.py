#!/usr/bin/env python3
"""The idea-pitch template the teams fill in on Friday: 4 slides, every box editable.

    python documents/make_pitch_template.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lxml import etree                                                    # noqa: E402
from pptx.dml.color import RGBColor                                       # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE                             # noqa: E402
from pptx.enum.shapes import MSO_SHAPE                                    # noqa: E402
from pptx.oxml.ns import qn                                               # noqa: E402
from pptx.util import Pt                                                  # noqa: E402

import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import ACCENT, PAPER, SOFT, X0, X1, T, card, head, p   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Idea_Pitch_Template.pptx'


def label(s, x, y, w, text, name):
    T(s, x, y, w, 18, p(text, 12.5, ACCENT, True, spc=1.6), name)


def box(s, x, y, w, h, name, size=20, pad_left=18):
    """An empty, see-through card the team clicks into and types; typing comes out white DM Sans."""
    sh = card(s, x, y, w, h, name)
    body = sh._element.find(qn('p:txBody'))
    if body is None:
        sh.text_frame                                       # makes the txBody
        body = sh._element.find(qn('p:txBody'))
    bpr = body.find(qn('a:bodyPr'))
    for k, v in {'wrap': 'square', 'lIns': str(int(pad_left * 12700)), 'rIns': '228600', 'tIns': '152400',
                 'bIns': '114300', 'anchor': 't'}.items():
        bpr.set(k, v)
    for old in body.findall(qn('a:p')):
        body.remove(old)
    para = etree.SubElement(body, qn('a:p'))
    ppr = etree.SubElement(para, qn('a:pPr'))
    ppr.set('algn', 'l')
    etree.SubElement(etree.SubElement(ppr, qn('a:lnSpc')), qn('a:spcPct')).set('val', '110000')
    end = etree.SubElement(para, qn('a:endParaRPr'))
    end.attrib.update({'lang': 'en-GB', 'sz': str(int(size * 100)), 'b': '0', 'dirty': '0'})
    etree.SubElement(etree.SubElement(end, qn('a:solidFill')), qn('a:srgbClr')).set('val', PAPER)
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        etree.SubElement(end, qn(tag)).set('typeface', KO.DM)
    return sh


def top(s, title):
    KO.base(s)
    T(s, X1 - 300, 34, 300, 20, p('IDEA PITCH  ·  TEAM _', 13, SOFT, True, spc=1.8, align='r'), 'Pitch label')
    T(s, X0, 92, X1 - X0, 70, head(title, size=60), 'Slide title')


# ===================================================================== slides
def cover(s):
    KO.base(s)
    T(s, X1 - 300, 34, 300, 20, p('IDEA PITCH  ·  TEAM _', 13, SOFT, True, spc=1.8, align='r'), 'Pitch label')
    # logo placeholder: a dashed square the team replaces with its logo
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(X0), Pt(130), Pt(170), Pt(170))
    sh.name = 'Logo placeholder'
    sh.adjustments[0] = 0.08
    sh.fill.background()
    sh.line.color.rgb = RGBColor.from_string(SOFT)
    sh.line.width = Pt(1.5)
    sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    sh.shadow.inherit = False
    K._plain(sh)
    T(s, X0, 130, 170, 170, p('YOUR LOGO', 18, SOFT, True, KO.BC, align='ctr'), 'Logo text', anchor='ctr')
    T(s, X0 + 200, 136, X1 - X0 - 200, 110, head('YOUR NAME', size=104, line=96), 'Name')
    T(s, X0 + 204, 244, X1 - X0 - 204, 60, p('Your one-line pitch', 26, PAPER, line=34), 'One-liner')
    label(s, X0, 352, X1 - X0, 'TEAM _', 'Team label')
    col = (X1 - X0) / 3
    for i in range(3):
        T(s, X0 + i * col, 380, col - 16, 70,
          [p('First name  ·  Role', 19, PAPER, line=28), p('First name  ·  Role', 19, PAPER, line=28)],
          f'Team column {i + 1}')
    KO.notes(s, 'Slide 1 of 4. One name for your product and your team, your logo, your one-line pitch, '
                'and the team: first name and role.\nAt most 6–7 minutes for the whole pitch.')


def problem(s):
    top(s, 'THE PROBLEM')
    label(s, X0, 176, X1 - X0, 'THE PROBLEM', 'Problem label')
    box(s, X0, 198, X1 - X0, 100, 'Problem')
    label(s, X0, 316, X1 - X0, 'THE USER', 'User label')
    box(s, X0, 338, X1 - X0, 60, 'User')
    label(s, X0, 416, X1 - X0, 'WHAT USERS TOLD US', 'Heard label')
    box(s, X0, 438, X1 - X0, 60, 'What users told us')
    KO.notes(s, 'Slide 2 of 4. One specific user with one specific problem: who spends how much time on which '
                'task, and why. If you spoke to a real person, say what they told you.')


def product(s):
    top(s, 'THE PRODUCT')
    label(s, X0, 176, X1 - X0, 'WHAT IT DOES', 'Product label')
    box(s, X0, 198, X1 - X0, 56, 'What it does')
    label(s, X0, 274, X1 - X0, 'KEY FEATURES', 'Features label')
    cw = (X1 - X0 - 2 * 14) / 3
    for i in range(3):
        x = X0 + i * (cw + 14)
        box(s, x, 296, cw, 100, f'Feature {i + 1}', size=17, pad_left=50)
        T(s, x + 18, 306, 26, 40, p(str(i + 1), 30, ACCENT, True, KO.BC, line=30), f'Feature {i + 1} number')
    label(s, X0, 416, X1 - X0, 'THE AI INSIDE', 'AI label')
    box(s, X0, 438, X1 - X0, 60, 'The AI inside')
    KO.notes(s, 'Slide 3 of 4. What the product does in one line, its three key features (the first one is '
                'the one that must work), and the exact job the AI does inside it.')


def business(s):
    top(s, 'THE BUSINESS CASE')
    cw = (X1 - X0 - 2 * 14) / 3
    for i, lab in enumerate(['WHO PAYS, HOW MUCH', 'WHY THEY SWITCH', 'RUNNING COST PER MONTH']):
        x = X0 + i * (cw + 14)
        label(s, x, 176, cw, lab, f'Box {i + 1} label')
        box(s, x, 198, cw, 150, lab.title(), size=18)
    label(s, X0, 372, X1 - X0, 'ON MONDAY, THIS WORKS LIVE', 'Monday label')
    box(s, X0, 394, X1 - X0, 80, 'On Monday')
    KO.notes(s, 'Slide 4 of 4. Who pays and how much, why they would switch from what they do today, and what it '
                'costs per month to run. For an idea inside a company: who backs it and whose budget pays.\n'
                'Then the one thing that will work live on Monday. The business mentors will ask about this.')


def build():
    prs = KO.new_deck()
    K.brand_links(prs)
    for make in (cover, problem, product, business):
        make(K.new_slide(prs))
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Idea pitch template'
    prs.core_properties.author = 'Example College'
    prs.core_properties.subject = 'Friday 23 October 2026, 13:00'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    print(build().name)
