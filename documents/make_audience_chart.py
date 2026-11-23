#!/usr/bin/env python3
"""The Audience Award slide: a native PowerPoint pie chart of the vote, in the team colours.

    python documents/make_audience_chart.py 12 8 5 9

The numbers are the votes for Team 1, 2, 3 and 4. With no numbers every slice is 0, to fill
in by hand: in PowerPoint, right-click the chart > Edit Data.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pptx.chart.data import CategoryChartData                             # noqa: E402
from pptx.dml.color import RGBColor                                       # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION   # noqa: E402
from pptx.util import Pt                                                  # noqa: E402

import make_day2 as D2                                                    # noqa: E402
import make_kickoff as KO                                                 # noqa: E402
import pptx_kit as K                                                      # noqa: E402
from make_kickoff import ACCENT, PAPER, SOFT, X0, T, head, kicker, p, Para, Run   # noqa: E402

OUT = HERE.parent / 'output' / 'documents' / 'Hackathon_Audience_Award.pptx'
TEAMS = [('Team 1', 'NoteRelay'), ('Team 2', 'StudyLoop'), ('Team 3', 'RenewRadar'), ('Team 4', 'ShipCheck')]
COLOURS = [KO.TEAM[n] for n in (1, 2, 3, 4)]


def chart_slide(s, votes):
    """The Audience Award slide on slide s (also used by make_awards.py)."""
    D2.base(s)

    kicker(s, 'AUDIENCE AWARD  ·  YOUR VOTE', 150, w=380)
    T(s, X0, 176, 380, 190, head('THE ROOM', 'HAS VOTED.', size=80, accent=(1,), line=76), 'Headline')
    total = sum(votes)
    top = max(votes)
    if total and votes.count(top) == 1:
        n = votes.index(top)
        T(s, X0, 352, 380, 30, p('WINNER', 13, SOFT, True, spc=1.8), 'Winner label')
        T(s, X0, 374, 380, 90, [p(f'{TEAMS[n][0]} – {TEAMS[n][1]}', 34, PAPER, True, KO.BC, line=36),
                                p(f'{top} of {total} votes ({int(top * 100 / total + 0.5)}%)', 17, SOFT, line=24)], 'Winner')

    data = CategoryChartData()
    data.categories = [f'{t} – {prod}' for t, prod in TEAMS]
    data.add_series('Votes', votes)
    frame = s.shapes.add_chart(XL_CHART_TYPE.PIE, Pt(440), Pt(92), Pt(470), Pt(420), data)
    frame.name = 'Audience vote'
    chart = frame.chart
    chart.has_title = False
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(15)
    chart.legend.font.name = KO.DM
    chart.legend.font.color.rgb = RGBColor.from_string(PAPER)
    plot = chart.plots[0]
    plot.has_data_labels = True
    labels = plot.data_labels
    labels.show_percentage = True
    labels.show_value = False
    labels.show_category_name = False
    labels.number_format = '0%'
    labels.number_format_is_linked = False
    labels.position = XL_LABEL_POSITION.CENTER
    labels.font.size = Pt(20)
    labels.font.name = KO.DM
    labels.font.bold = True
    labels.font.color.rgb = RGBColor.from_string('121316')
    for i, colour in enumerate(COLOURS):
        point = plot.series[0].points[i]
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = RGBColor.from_string(colour)
        point.format.line.color.rgb = RGBColor.from_string('121316')
        point.format.line.width = Pt(1.5)
    # Own labels, rounded like Slido (PowerPoint would make two equal shares 13% and 14% to reach 100%)
    if total:
        for i, v in enumerate(votes):
            dl = plot.series[0].points[i].data_label
            dl.text_frame.text = f'{int(v * 100 / total + 0.5)}%'
            run = dl.text_frame.paragraphs[0].runs[0]
            run.font.size = Pt(20)
            run.font.bold = True
            run.font.name = KO.DM
            run.font.color.rgb = RGBColor.from_string('121316')
            dl.position = XL_LABEL_POSITION.CENTER

    KO.notes(s, 'Audience Award. The numbers come from the Slido poll "Audience Award: which product would you use?". '
                'To change them: right-click the chart > Edit Data.')


def build(votes):
    D2.make_dark_bg()
    prs = KO.new_deck()
    chart_slide(K.new_slide(prs), votes)
    prs.core_properties.title = 'AI Entrepreneurship Hackathon — Audience Award'
    prs.core_properties.author = 'Example College'
    prs.save(OUT)
    return OUT


if __name__ == '__main__':
    args = [int(a) for a in sys.argv[1:]]
    if args and len(args) != 4:
        sys.exit('Give four numbers: the votes for Team 1, 2, 3 and 4.')
    print(build(args or [0, 0, 0, 0]).name)
