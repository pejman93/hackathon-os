#!/usr/bin/env python3
"""Email logo for the hackathon mailbox, in two shapes: a square profile picture and a wide logo for the signature.

    python marketing/email-logo/make-email-logo.py
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[1]
OUT = HERE.parents[1] / 'output' / 'marketing' / 'email-logo'
OUT.mkdir(parents=True, exist_ok=True)
FONTS = PROJ / 'brand' / 'fonts'
LOGO = PROJ / 'website' / 'assets' / 'logo.png'

INK, PAPER, WHITE = (0x12, 0x13, 0x16), (0xf2, 0xf1, 0xe9), (0xff, 0xff, 0xff)
ACCENT, BRAND = (0x7e, 0x98, 0xff), (0x14, 0x1a, 0x9d)

SS = 3            # draw at 3x and reduce, so every edge is properly anti-aliased
SAFE = 0.84       # share of the circle's radius the artwork may reach


# ------------------------------------------------------------------ pieces
def logo_mask(width):
    """The Example College logo as a coverage mask, cropped to its ink, `width` px wide."""
    a = Image.open(LOGO).convert('RGBA').split()[3]
    a = a.crop(a.point(lambda v: 255 if v > 16 else 0).getbbox())
    big = a.resize((width, round(width * a.height / a.width)), Image.LANCZOS)
    k = np.asarray(big, dtype=np.float32) / 255
    k = np.clip((k - 0.5) * 3.2 + 0.5, 0, 1)          # steepen the soft enlarged edge
    return Image.fromarray((k * 255).round().astype(np.uint8), 'L')


def text_mask(text, font_file, width, tracking=0.0):
    """`text` as a coverage mask whose INK is exactly `width` px wide.
    `tracking` is extra space between letters, in em."""
    def render(size):
        font = ImageFont.truetype(str(FONTS / font_file), size)
        adv = [font.getlength(ch) for ch in text]
        step = tracking * size
        total = math.ceil(sum(adv) + step * (len(text) - 1)) + 2 * size
        im = Image.new('L', (total, size * 2), 0)
        d = ImageDraw.Draw(im)
        x = size
        for ch, a in zip(text, adv):
            d.text((x, size // 2), ch, font=font, fill=255)
            x += a + step
        return im.crop(im.getbbox())
    size = 400
    for _ in range(4):                                  # ink width is linear in size
        size = max(8, round(size * width / render(size).width))
    m = render(size)
    return m if m.width == width else m.resize((width, round(m.height * width / m.width)), Image.LANCZOS)


def paint(canvas, mask, xy, colour):
    layer = Image.new('RGBA', mask.size, colour + (255,))
    layer.putalpha(mask)
    canvas.alpha_composite(layer, (round(xy[0]), round(xy[1])))


def finish(canvas, size, path):
    canvas.resize(size, Image.LANCZOS).save(path, optimize=True)
    print(f'  {path.relative_to(PROJ)}  {size[0]} x {size[1]}')


# ------------------------------------------------------- 1. profile picture
def profile(name, ground, logo_colour, word_colour, px=1024):
    c = px * SS
    w = round(c * 0.70)                                 # logo and word share one width
    logo = logo_mask(w)
    word = text_mask('HACKATHON', 'BarlowCondensed-800.ttf', w, tracking=0.012)
    gap = round(w * 0.085)
    h = logo.height + gap + word.height
    x, y = (c - w) / 2, (c - h) / 2

    # a circle, not a square, is what is finally shown: test the block's corners
    reach = math.hypot(w / 2, h / 2) / (c / 2)
    assert reach <= SAFE, f'artwork reaches {reach:.0%} of the radius, limit {SAFE:.0%}'

    canvas = Image.new('RGBA', (c, c), ground + (255,))
    paint(canvas, logo, (x, y), logo_colour)
    paint(canvas, word, (x, y + logo.height + gap), word_colour)
    finish(canvas.convert('RGB'), (px, px), OUT / f'hackathon-email-logo-{name}.png')
    return reach


# ------------------------------------------------------------ 2. signature
def signature(name, ground, logo_colour, text_colour, word_colour, rule_colour, logo_h=132):
    lh = logo_h * SS
    logo = logo_mask(round(lh * 362 / 106))
    lh = logo.height
    # the two lines of type fill the logo's own height: small line on its top
    # edge, HACKATHON standing on its bottom edge, both the same width
    word_h = round(lh * 0.66)
    probe = text_mask('HACKATHON', 'BarlowCondensed-800.ttf', 1000, tracking=0.012)
    tw = round(1000 * word_h / probe.height)
    word = text_mask('HACKATHON', 'BarlowCondensed-800.ttf', tw, tracking=0.012)
    small = text_mask('AI ENTREPRENEURSHIP', 'DMSans-700.ttf', tw, tracking=0.16)

    slant, before, after = lh * 0.24, lh * 0.30, lh * 0.34
    pad_x, pad_y = (round(lh * 0.46), round(lh * 0.42)) if ground else (round(lh * 0.06), round(lh * 0.06))
    width = pad_x * 2 + logo.width + round(before + slant + after) + tw
    height = pad_y * 2 + lh
    canvas = Image.new('RGBA', (width, height), (ground + (255,)) if ground else (0, 0, 0, 0))

    paint(canvas, logo, (pad_x, pad_y), logo_colour)
    dx = pad_x + logo.width + before
    ImageDraw.Draw(canvas).line([(dx, pad_y + lh), (dx + slant, pad_y)], fill=rule_colour, width=max(2, round(lh * 0.014)))
    tx = dx + slant + after
    paint(canvas, small, (tx, pad_y), text_colour)
    paint(canvas, word, (tx, pad_y + lh - word.height), word_colour)
    out = (round(width / SS), round(height / SS))
    finish(canvas if not ground else canvas.convert('RGB'), out, OUT / f'hackathon-email-signature-{name}.png')


if __name__ == '__main__':
    print('profile picture (shown as a circle):')
    for name, ground, lc, wc in [('dark', INK, WHITE, ACCENT),
                                 ('light', PAPER, BRAND, INK),
                                 ('blue', BRAND, WHITE, WHITE)]:
        reach = profile(name, ground, lc, wc)
    print(f'  artwork reaches {reach:.0%} of the circle radius (limit {SAFE:.0%})')
    print('signature / mail header:')
    signature('dark', INK, WHITE, PAPER, ACCENT, (0xf2, 0xf1, 0xe9, 140))
    signature('light', None, BRAND, INK, INK, (0x12, 0x13, 0x16, 120))
