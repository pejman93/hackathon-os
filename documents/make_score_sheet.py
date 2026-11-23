#!/usr/bin/env python3
"""The paper score sheet for the judges (backup for the judging form): A4 landscape.

    python documents/make_score_sheet.py

Same criteria, weights and 1-5 scale as backend/judging/Judging.gs.
"""
import pathlib

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FONTS = ROOT / 'brand' / 'fonts'
OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Judging_Score_Sheet.pdf'
FORM_URL = 'https://example.org/link'

for name, file in (('DM', 'DMSans-400.ttf'), ('DMB', 'DMSans-700.ttf'), ('BC', 'BarlowCondensed-700.ttf')):
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))

INK, GREY, RULE, BLUE = (0.07, 0.07, 0.09), (0.36, 0.38, 0.41), (0.78, 0.78, 0.80), (0.08, 0.10, 0.62)
TEAMS = ['Team 1', 'Team 2', 'Team 3', 'Team 4']
CRITERIA = [('Working product', 30, 'It works live, with real AI inside.'),
            ('Real problem, real user', 20, 'A specific person or role with a real problem.'),
            ('Business case', 20, 'Who pays, how much, and why they would switch.'),
            ('Sustainability', 15, 'Monthly running cost, and what it depends on.'),
            ('Demo and pitch', 15, 'A clear story, on time.')]


def build():
    W, H = landscape(A4)
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle('Judging score sheet – AI Entrepreneurship Hackathon')
    c.setAuthor('Example College')
    m = 40

    def text(x, y, s, font='DM', size=10, color=INK, anchor='l'):
        c.setFont(font, size)
        c.setFillColorRGB(*color)
        {'l': c.drawString, 'c': c.drawCentredString, 'r': c.drawRightString}[anchor](x, y, s)

    # heading
    text(m, H - m - 18, 'JUDGING SCORE SHEET', 'BC', 24, BLUE)
    text(m, H - m - 36, 'AI Entrepreneurship Hackathon  ·  Monday 26 October 2026  ·  Example Campus', 'DM', 10, GREY)
    text(W - m - 260, H - m - 18, 'Judge:', 'DMB', 11)
    c.setStrokeColorRGB(*INK)
    c.setLineWidth(0.6)
    c.line(W - m - 218, H - m - 20, W - m, H - m - 20)
    text(m, H - m - 62, 'Score each criterion from 1 (weak) to 5 (excellent): circle one number per team. '
                        'Score on your own first, then compare.', 'DM', 10.5)

    # table
    x0, top = m, H - m - 84
    col0, colw = 250, (W - 2 * m - 250) / 4
    head_h, row_h, total_h, note_h = 26, 46, 34, 74
    rows_y = [top - head_h - i * row_h for i in range(len(CRITERIA) + 1)]
    bottom = rows_y[-1] - total_h - note_h

    c.setFillColorRGB(0.93, 0.94, 1.0)
    c.rect(x0, top - head_h, W - 2 * m, head_h, stroke=0, fill=1)
    text(x0 + 10, top - 17, 'Criterion', 'DMB', 10.5)
    for i, team in enumerate(TEAMS):
        text(x0 + col0 + colw * (i + 0.5), top - 17, team, 'DMB', 10.5, anchor='c')

    for r, (name, weight, what) in enumerate(CRITERIA):
        y = rows_y[r]
        text(x0 + 10, y - 19, f'{name}  ({weight}%)', 'DMB', 11)
        text(x0 + 10, y - 34, what, 'DM', 8.8, GREY)
        for i in range(4):
            cx = x0 + col0 + colw * (i + 0.5)
            for k in range(5):
                text(cx + (k - 2) * 22, y - 28, str(k + 1), 'DM', 12, anchor='c')

    y = rows_y[-1]
    text(x0 + 10, y - 21, 'Total (out of 100)', 'DMB', 11)
    y -= total_h
    text(x0 + 10, y - 19, 'Notes', 'DMB', 11)
    text(x0 + 10, y - 34, 'Optional', 'DM', 8.8, GREY)

    # grid
    c.setStrokeColorRGB(*RULE)
    c.setLineWidth(0.6)
    for yy in [top] + [top - head_h] + rows_y[1:] + [rows_y[-1] - total_h, bottom]:
        c.line(x0, yy, W - m, yy)
    for i in range(5):
        xx = x0 + col0 + colw * i
        c.line(xx, top, xx, bottom)
    c.line(x0, top, x0, bottom)
    c.line(W - m, top, W - m, bottom)

    # how the total works
    text(m, bottom - 22, 'Total = Working product × 6 + Real problem × 4 + Business case × 4 + Sustainability × 3 '
                         '+ Demo and pitch × 3.', 'DM', 9.5, GREY)
    # QR code to the judging form, bottom right
    import io
    import segno
    from reportlab.lib.utils import ImageReader
    buf = io.BytesIO()
    segno.make(FORM_URL, error='m').save(buf, kind='png', scale=10, border=1)
    buf.seek(0)
    q = 58
    c.drawImage(ImageReader(buf), W - m - q, m - 6, q, q)
    text(W - m - q - 8, m + 30, 'Judging form', 'DMB', 9.5, anchor='r')
    text(W - m - q - 8, m + 17, FORM_URL.replace('https://', ''), 'DM', 9, GREY, anchor='r')
    text(W - m - q - 8, m + 4, 'Please enter your scores in the judging form as well.', 'DM', 9, GREY, anchor='r')
    c.showPage()
    c.save()
    return OUT


if __name__ == '__main__':
    print(build().name)
