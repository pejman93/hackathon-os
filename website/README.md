# Website

The event site as plain HTML, CSS and JavaScript, with no framework and no build step. It runs as an
application page before the event and as a recap afterwards.

Open [`index.html`](index.html) in a browser to try it. With no endpoint set, the forms run in
**preview mode**: they behave normally, nothing is sent, and the page says so.

## Go live

1. Deploy [`backend/applications`](../backend/applications) and [`backend/signups`](../backend/signups).
2. Build one paste-ready page for a WordPress (Elementor) HTML widget:

```bash
HACKATHON_ENDPOINT=https://script.google.com/macros/s/.../exec \
HACKATHON_SIGNUP_ENDPOINT=https://script.google.com/macros/s/.../exec \
HACKATHON_UPLOADS=https://your-site.example/wp-content/uploads/2026/10/ \
python website/wordpress/build.py
```

The result is `output/website/hackathon-elementor.html`. The build refuses to run without real
endpoints, so a page that says "preview" can never be published by accident.
