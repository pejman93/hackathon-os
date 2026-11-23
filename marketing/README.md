# Marketing

The campaign, generated from the brand file. Change a colour, date or link and rebuild.

```bash
python tools/build_all.py marketing
```

| Folder | What it makes |
|---|---|
| [`posters/`](posters) | A4 QR posters as vector PDF |
| [`screens/`](screens), [`split/`](split), [`social/`](social) | 16:9 artwork for venue screens and TVs |
| [`instagram/`](instagram) | Carousels with a background that runs across slides, and stories |
| [`event-table/`](event-table) | Printable demo-table signs |
| [`email-banner/`](email-banner) | Animated GIF banners from a small JSON job file |
| [`email-logo/`](email-logo) | Mailbox profile picture and signature logo |

The layout code checks its own work: overlapping elements, text outside safe areas, and QR codes
too close to other artwork are reported at build time.
