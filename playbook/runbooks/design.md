# Design

## The brand

- [`brand/brand.json`](../../brand/brand.json) holds the colours, fonts, logos and style rules. Change
  them there, never in a script.
- [`brand/brand.py`](../../brand/brand.py) loads them: `brand.load().rgb('accent')`,
  `.font('display', 800)`, `.logo('white')`. Pass an event's override to `load()` to change one
  edition only.

## Tools

- `marketing/email-banner/make_banner.py JOB.json --out FOLDER`. Copy a file from `jobs/` and change
  the words, picture and output.
- `print-kit/`, `documents/` and the other `marketing/` folders each build from their own data.

## House style

- Ink, paper and one strong blue. Few labels, each fact once, no filler. Pictures light and clean.
- Guides and plans: white, one blue, thin grey table lines, no tinted boxes.
- Email banners: 1200 x 400 shown at 600 x 200. The first frame is the finished picture.
- A deck that mirrors a page copies that page's look. Presented slides: no money, no first person.

## Check before sharing

Open every result and look at it. Measure what can be measured: text inside its box, sizes and file
size.
