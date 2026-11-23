#!/usr/bin/env python3
"""Animated email banner from a small job file.

Colours, fonts and logos come from brand/brand.json. The words, the photo and the output name come
from a job file (see jobs/). Paths in a job are relative to the repository root.

    python marketing/email-banner/make_banner.py marketing/email-banner/jobs/demo-night.json

The banner shows:

    LINE 1 of scene 1             YOU BUILT IT.
    BEFORE + VERB + AFTER         NOW SHOW IT. -> NOW DEMO IT. -> ...
    then scene 2 rolls in         ONE TABLE. / REAL USERS. and back to the start

Three rules keep it safe in real inboxes:
1. The FIRST frame is the finished picture. Older Outlook shows only the first frame.
2. Nothing a reader needs is only in the picture: dates, place and links are in the email text.
3. The file stays small: one shared palette, the photo dithered once, and later frames store only
   the rolling words and the dot.
"""
import argparse
import json
import math
import pathlib
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'brand'))
import brand  # noqa: E402

ROOT = brand.ROOT

W, H = 1200, 400              # shown at 600 x 200 in the email
SS = 2                        # drawn at twice that size, then reduced, for clean edges
PANEL = 620                   # the photo fills x 0..620 and fades into ink over its last 230 px
X0 = 652                      # left edge of the words
MAX_W = W - 48 - X0           # the words never reach the photo, so they always sit on flat ink

# Set by setup() from the brand and the job.
INK = PAPER = WHITE = ACCENT = BRAND = CORAL = MUTED = None
BC800 = DM700 = LOGO = MARK = PHOTO = None
JOB = {}


def setup(job, config=None):
    global INK, PAPER, WHITE, ACCENT, BRAND, CORAL, MUTED, BC800, DM700, LOGO, MARK, PHOTO, JOB
    B = brand.load(config)
    INK, PAPER, WHITE = B.rgb('ink'), B.rgb('paper'), B.rgb('white')
    ACCENT, BRAND, CORAL, MUTED = B.rgb('accent'), B.rgb('brand_blue'), B.rgb('coral'), B.rgb('muted')
    BC800, DM700 = B.font('display', 800), B.font('text', 700)
    LOGO = B.logo('white')
    MARK = B.logo(job['partner_mark']['logo'])
    PHOTO = ROOT / job['photo']
    JOB = job


def scene1(verb):
    s1 = JOB['scene1']
    return [(s1['line1'], PAPER)], [(s1['line2_before'], PAPER), (verb, ACCENT), (s1['line2_after'], PAPER)]


def scene2():
    s2 = JOB['scene2']
    return [(s2['line1'], PAPER)], [(s2['line2'], ACCENT)]


def s(v):
    return int(round(v * SS))


def font(path, size):
    return ImageFont.truetype(str(path), s(size))


def text_sprite(runs, font_file, size, track=0.0):
    """runs: [(text, colour)] on one line, with optional letter spacing. Returns a tight RGBA image."""
    f = font(font_file, size)
    step = s(track)
    chars = [(ch, col) for text, col in runs for ch in text]
    adv = [f.getlength(ch) for ch, _ in chars]
    width = int(sum(adv) + step * (len(chars) - 1)) + s(size)
    im = Image.new('RGBA', (width, s(size * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = s(size * 0.25)
    for (ch, col), a in zip(chars, adv):
        d.text((x, s(size * 0.4)), ch, font=f, fill=col + (255,))
        x += a + step
    return im.crop(im.getbbox())


def word(text, colour, f):
    """One word on a fixed baseline, so words placed side by side line up exactly."""
    asc, desc = f.getmetrics()
    im = Image.new('RGBA', (int(math.ceil(f.getlength(text))) + s(6), asc + desc), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), text, font=f, fill=colour + (255,))
    return im


def faded(sprite, alpha):
    if alpha >= 0.999:
        return sprite
    out = sprite.copy()
    out.putalpha(sprite.getchannel('A').point(lambda v: int(v * alpha)))
    return out


# ------------------------------------------------------------------ the still parts
def photo_ground():
    """Ink, with the photo on the left fading into it, and soft shades top and bottom."""
    base = Image.new('RGBA', (s(W), s(H)), INK + (255,))
    src = Image.open(PHOTO).convert('RGB')
    sw, sh = src.size
    ch = int(sw * H / PANEL)
    top = max(0, (sh - ch) // 2)
    ph = src.crop((0, top, sw, top + min(ch, sh))).resize((s(PANEL), s(H)), Image.LANCZOS)
    ph = ImageEnhance.Color(ph).enhance(0.84)
    ph = ImageEnhance.Contrast(ph).enhance(1.06)
    ph = ImageEnhance.Brightness(ph).enhance(0.9)
    ph = Image.blend(ph, ImageChops.multiply(ph, Image.new('RGB', ph.size, (222, 228, 255))), 0.6)

    fade_from, fade_to = PANEL - 230, PANEL
    row = Image.new('L', (ph.width, 1))
    for x in range(ph.width):
        t = min(1.0, max(0.0, (x / SS - fade_from) / (fade_to - fade_from)))
        row.putpixel((x, 0), int(255 * (1 - t * t * (3 - 2 * t))))
    base.paste(ph, (0, 0), row.resize(ph.size))

    shade = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for y in range(s(150)):
        a = (1 - y / s(150)) ** 1.5 * 0.8
        d.line([(0, y), (s(PANEL), y)], fill=INK + (int(255 * a),))
    for y in range(s(80)):
        a = (y / s(80)) ** 1.6 * 0.6
        d.line([(0, s(H) - s(80) + y), (s(PANEL), s(H) - s(80) + y)], fill=INK + (int(255 * a),))
    base.alpha_composite(shade)
    return base


def chrome(im):
    """Logo lockup top left, partner mark top right, photo credit bottom left."""
    over = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    logo = Image.open(LOGO).convert('RGBA')
    lw, top = 150, 28
    lh = lw * logo.height / logo.width
    over.alpha_composite(logo.resize((s(lw), s(lh)), Image.LANCZOS), (s(48), s(top)))
    dx = 48 + lw + 20
    d.line([(s(dx), s(top + lh - 4)), (s(dx + 12), s(top + 4))], fill=MUTED + (150,), width=s(1.4))
    tx = dx + 27
    over.alpha_composite(text_sprite([(JOB['lockup']['small'], PAPER)], DM700, 10, 0.4), (s(tx), s(top + lh * 0.24)))
    over.alpha_composite(text_sprite([(JOB['lockup']['big'], PAPER)], BC800, 21), (s(tx), s(top + lh * 0.50)))
    mark_img = Image.open(MARK).convert('RGBA')
    mark_h = 54
    ratio = mark_img.width / mark_img.height
    mark = mark_img.resize((s(mark_h * ratio), s(mark_h)), Image.LANCZOS)
    mx = W - 48 - mark_h * ratio
    over.alpha_composite(mark, (s(mx), s(top + lh / 2 - mark_h / 2)))
    if JOB['partner_mark'].get('label'):
        lab = text_sprite([(JOB['partner_mark']['label'], PAPER)], DM700, 9, 1.6)
        over.alpha_composite(lab, (s(mx - 14) - lab.width, int(s(top + lh / 2) - lab.height / 2)))
    if JOB.get('photo_credit'):
        credit = faded(text_sprite([(JOB['photo_credit'], PAPER)], DM700, 10, 1.2), 0.72)
        over.alpha_composite(credit, (s(48), s(H - 22) - credit.height))
    im.alpha_composite(over)


# ------------------------------------------------------------------ the words
def layout():
    """Pick one headline size so every line fits MAX_W, then centre the block in the free height."""
    s1, s2 = JOB['scene1'], JOB['scene2']
    size = 112
    while True:
        f = font(BC800, size)
        sp = f.getlength(' ')
        lines = [s1['line1'], s2['line1'], s2['line2']] + \
                [f"{s1['line2_before']}{v}{s1['line2_after']}" for v in s1['verbs']]
        if max(f.getlength(t) for t in lines) <= s(MAX_W) or size <= 40:
            break
        size -= 2
    asc, desc = f.getmetrics()
    cap_top, cap_bottom = f.getbbox('H')[1], f.getbbox('H')[3]
    cap = (cap_bottom - cap_top) / SS
    eyebrow = text_sprite([(JOB['eyebrow'], ACCENT)], DM700, 15, 2.2)
    eb_h = eyebrow.height / SS
    gap_eb, gap_lines = 24, cap * 0.30
    block = eb_h + gap_eb + cap + gap_lines + cap
    zone_top, zone_bottom = 108, H - 30
    y_eb = zone_top + (zone_bottom - zone_top - block) / 2
    cap1 = y_eb + eb_h + gap_eb
    cap2 = cap1 + cap + gap_lines
    return dict(f=f, size=size, sp=sp, asc=asc, cap_top_px=cap_top, cap=cap, eyebrow=eyebrow,
                y_eb=y_eb, cap1=cap1, cap2=cap2)


def static_frame(L):
    im = photo_ground()
    chrome(im)
    im.alpha_composite(L['eyebrow'], (s(X0 + 22), s(L['y_eb'])))
    return im


def dot_centre(L):
    return X0 + 7, L['y_eb'] + L['eyebrow'].height / SS / 2


def line_sprite(runs, f):
    width = int(sum(f.getlength(t) for t, _ in runs)) + s(10)
    asc, desc = f.getmetrics()
    im = Image.new('RGBA', (width, asc + desc), (0, 0, 0, 0))
    x = 0
    for text, col in runs:
        im.alpha_composite(word(text, col, f), (int(round(x)), 0))
        x += f.getlength(text)
    return im


def ease_out(t):
    return 1 - (1 - min(1.0, max(0.0, t))) ** 3


def roll_line(im, L, cap_top, old, new, t):
    """Old line rolls up and out, new line rolls up and in, clipped to the line's own band."""
    f = L['f']
    e = ease_out(t)
    y = s(cap_top) - L['cap_top_px']
    band_top, band_h = s(cap_top - 10), s(L['cap'] + 20)
    band = Image.new('RGBA', (s(W - X0), band_h), (0, 0, 0, 0))
    roll = band_h * 0.95
    for runs, dy, alpha in ((old, -e * roll, (1 - e) ** 2), (new, (1 - e) * roll, e ** 0.7)):
        if runs and alpha > 0.003:
            band.alpha_composite(faded(line_sprite(runs, f), alpha), (0, int(round(y - band_top + dy))))
    im.alpha_composite(band, (s(X0), band_top))


def roll_verb(im, L, a, b, t):
    """Line 2 of scene 1: the first word stays, the verb rolls a -> b, the end slides to its new place."""
    f = L['f']
    s1 = JOB['scene1']
    before, after = s1['line2_before'], s1['line2_after']
    e = ease_out(t)
    y2 = s(L['cap2']) - L['cap_top_px']
    im.alpha_composite(word(before.rstrip(), PAPER, f), (s(X0), y2))
    x_verb = s(X0) + int(round(f.getlength(before)))
    band_top, band_h = s(L['cap2'] - 10), s(L['cap'] + 20)
    band = Image.new('RGBA', (s(W - X0), band_h), (0, 0, 0, 0))
    roll = band_h * 0.95
    for verb, dy, alpha in ((a, -e * roll, (1 - e) ** 2), (b, (1 - e) * roll, e ** 0.7)):
        if alpha > 0.003:
            band.alpha_composite(faded(word(verb, ACCENT, f), alpha), (0, int(round(y2 - band_top + dy))))
    im.alpha_composite(band, (x_verb, band_top))
    wa, wb = f.getlength(a), f.getlength(b)
    lead = len(after) - len(after.lstrip(' '))
    x_end = x_verb + wa + (wb - wa) * e + L['sp'] * lead
    im.alpha_composite(word(after.lstrip(' '), PAPER, f), (int(round(x_end)), y2))


def draw_dynamic(im, L, step, pulse):
    """step is ('verb', a, b, t) inside scene 1, or ('scene', old, new, t1, t2) for both lines."""
    if step[0] == 'verb':
        _, a, b, t = step
        roll_line(im, L, L['cap1'], None, scene1(b)[0], 1.0)
        roll_verb(im, L, a, b, t)
    else:
        _, old, new, t1, t2 = step
        roll_line(im, L, L['cap1'], old[0], new[0], t1)
        roll_line(im, L, L['cap2'], old[1], new[1], t2)

    cx, cy = dot_centre(L)
    over = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    if pulse > 0.06:
        r = 5.5 + 12 * pulse
        al = int(255 * 0.85 * (1 - pulse) ** 1.4)
        d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], outline=CORAL + (al,), width=s(2))
    d.ellipse([s(cx - 5.5), s(cy - 5.5), s(cx + 5.5), s(cy + 5.5)], fill=CORAL + (255,))
    im.alpha_composite(over)


def dynamic_boxes(L, scale=1.0):
    """Areas that change between frames, in output pixels. Both sit on flat ink."""
    cx, cy = dot_centre(L)
    dot = (cx - 22, cy - 22, cx + 22, cy + 22)
    words = (X0 - 4, L['cap1'] - 12, W - 8, L['cap2'] + L['cap'] + 12)
    return [tuple(int(round(v * scale)) for v in box) for box in (dot, words)]


# ------------------------------------------------------------------ the timeline
def timeline():
    """(ms, step, pulse). Frame 1 is the finished picture: scene 1 with the first verb, dot at rest."""
    verbs = JOB['scene1']['verbs']
    period, hold_step, roll_step = 960, 160, 50
    steps = []

    def hold(step, ms):
        for _ in range(ms // hold_step):
            steps.append((hold_step, step))

    def verb(a, b, ms_after):
        for k in range(1, 6):
            steps.append((roll_step, ('verb', a, b, k / 5)))
        hold(('verb', b, b, 1.0), ms_after)

    def scene(old, new, ms_after):
        for k in range(1, 7):                      # line 2 follows line 1 one frame later
            steps.append((roll_step, ('scene', old, new, min(1, k / 5), min(1, max(0, (k - 1) / 5)))))
        hold(('scene', new, new, 1.0, 1.0), ms_after)

    hold(('verb', verbs[0], verbs[0], 1.0), 1760)
    for i in range(len(verbs) - 1):
        verb(verbs[i], verbs[i + 1], 1120 if i == len(verbs) - 2 else 800)
    scene(scene1(verbs[-1]), scene2(), 1760)
    scene(scene2(), scene1(verbs[0]), 0)           # back where the loop starts
    out, clock = [], 0
    for ms, step in steps:
        out.append((ms, step, (clock % period) / period))
        clock += ms
    return out


# ------------------------------------------------------------------ GIF
def palette_for(still, panel_px):
    fixed = [INK, PAPER, ACCENT, CORAL, MUTED, BRAND, WHITE]
    ramps = []
    for c in (PAPER, ACCENT, CORAL):
        for k in range(1, 12):
            a = k / 12
            ramps.append(tuple(int(round(INK[i] * (1 - a) + c[i] * a)) for i in range(3)))
    n = 256 - len(fixed) - len(ramps)
    q = still.crop((0, 0, panel_px, still.height)).quantize(colors=n, method=Image.Quantize.MEDIANCUT,
                                                             dither=Image.Dither.NONE)
    flat = [v for c in fixed + ramps for v in c] + q.getpalette()[:n * 3]
    flat += list(INK) * ((768 - len(flat)) // 3)
    pal = Image.new('P', (1, 1))
    pal.putpalette(flat[:768])
    return pal


def save_gif(frames, durations, boxes, panel_px, path):
    still = frames[0]
    pal = palette_for(still, panel_px)
    base = still.quantize(palette=pal, dither=Image.Dither.NONE)
    base.paste(still.crop((0, 0, panel_px, still.height)).quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG),
               (0, 0))
    out = []
    for fr in frames:
        p = base.copy()
        for box in boxes:
            p.paste(fr.crop(box).quantize(palette=pal, dither=Image.Dither.NONE), box[:2])
        out.append(p)
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0,
                optimize=False, disposal=1)
    return path


def build():
    L = layout()
    still = static_frame(L)
    frames, durations = [], []
    for ms, step, pulse in timeline():
        im = still.copy()
        draw_dynamic(im, L, step, pulse)
        frames.append(im.convert('RGB').resize((W, H), Image.LANCZOS))
        durations.append(ms)
    return L, frames, durations


def main():
    ap = argparse.ArgumentParser(description='Animated email banner from a job file.')
    ap.add_argument('job', help='job file (JSON), see jobs/')
    ap.add_argument('--config', help='a JSON file whose "brand" block overrides brand.json')
    ap.add_argument('--out', help='output folder (default: the job\'s output.folder)')
    a = ap.parse_args()
    job = json.loads(pathlib.Path(a.job).read_text(encoding='utf-8'))
    setup(job, a.config)
    out = pathlib.Path(a.out) if a.out else ROOT / job['output']['folder']
    out.mkdir(parents=True, exist_ok=True)
    name = job['output']['name']
    L, frames, durations = build()
    big = save_gif(frames, durations, dynamic_boxes(L), PANEL, out / f'{name}.gif')
    half = [f.resize((W // 2, H // 2), Image.LANCZOS) for f in frames]
    small = save_gif(half, durations, dynamic_boxes(L, 0.5), PANEL // 2, out / f'{name}-600px.gif')
    frames[0].save(out / f'{name}-still.png')
    for p in (big, small, out / f'{name}-still.png'):
        print(f'{p.name:40} {p.stat().st_size / 1024:7.0f} KB')
    print(f'{len(frames)} frames, one loop lasts {sum(durations) / 1000:.1f} s, headline {L["size"]} px')


if __name__ == '__main__':
    main()
