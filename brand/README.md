# Brand

[`brand.json`](brand.json) holds the colours, fonts, logos and style rules. [`brand.py`](brand.py)
loads them, with an optional override for a single event:

```python
import brand
b = brand.load()                 # or brand.load("my-event.json")
b.rgb("accent"); b.font("display", 800); b.logo("white")
```

The logo and partner marks belong to a made-up college and are drawn by
[`tools/make_demo_assets.py`](../tools/make_demo_assets.py).

Fonts: [Barlow](https://github.com/jpt/barlow) and [DM Sans](https://github.com/googlefonts/dm-fonts),
under the SIL Open Font License ([`OFL-Barlow.txt`](fonts/OFL-Barlow.txt),
[`OFL-DMSans.txt`](fonts/OFL-DMSans.txt)).
