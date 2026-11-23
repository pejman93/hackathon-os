#!/usr/bin/env python3
"""Build one paste-ready page for a WordPress (Elementor) HTML widget from website/.

What it does, and nothing else:
  1. inlines styles.css and host.css into one <style>
  2. inlines config.js, team.js, app.js and mentor.js into four <script> blocks
  3. rewrites assets/... to your Media Library URLs
  4. sets the two form endpoints
  5. strips the DESIGN PREVIEW banner from the markup

Step 5 is not cosmetic. The banner is removed at runtime by JavaScript, but
link-preview crawlers (WhatsApp, LinkedIn, Facebook) never run scripts, so a
banner left in the markup makes every share of the live page say that nothing
is stored.

Usage:
    python website/wordpress/build.py --preview

    HACKATHON_ENDPOINT=https://script.google.com/macros/s/.../exec \\
    HACKATHON_SIGNUP_ENDPOINT=https://script.google.com/macros/s/.../exec \\
    HACKATHON_UPLOADS=https://your-site.example/wp-content/uploads/2026/10/ \\
    python website/wordpress/build.py

--preview needs no endpoints: the forms stay in preview mode and nothing is sent.
A live build refuses to run without real endpoints, so a page whose forms answer
"preview, nothing saved" can never be published by accident.
"""
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / "website"
OUT = ROOT / "output" / "website" / "hackathon-elementor.html"

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Barlow+Condensed:wght@600;700;800&family=DM+Sans:wght@400;500;600;700"
    "&display=swap"
)
BANNER = (
    '<div class="preview-banner">DESIGN PREVIEW '
    "<span>Try the full experience. No application is sent or stored.</span></div>\n"
)
EXEC_URL = re.compile(r"https://script\.google\.com/macros/s/[\w-]+/exec")


def read(rel):
    return (SITE / rel).read_text(encoding="utf-8")


def endpoint(name):
    value = os.environ.get(name, "")
    if not EXEC_URL.fullmatch(value):
        raise SystemExit(f"error: {name} must be a deployed Apps Script /exec URL (or use --preview).")
    return value


def build(preview):
    body = read("index.html")
    body = body[body.index("<body>") + len("<body>"): body.index("</body>")]
    if BANNER not in body:
        raise SystemExit("error: the DESIGN PREVIEW banner was not found in website/index.html.")

    config = read("config.js")
    if preview:
        uploads = recap_uploads = "../../website/assets/"
        recap_uploads += "recap/"
    else:
        body = body.replace(BANNER, "")
        config = config.replace("endpoint: ''", f"endpoint: '{endpoint('HACKATHON_ENDPOINT')}'")
        config = config.replace("signupEndpoint: ''", f"signupEndpoint: '{endpoint('HACKATHON_SIGNUP_ENDPOINT')}'")
        uploads = os.environ.get("HACKATHON_UPLOADS", "")
        if not uploads.startswith("https://") or not uploads.endswith("/"):
            raise SystemExit("error: HACKATHON_UPLOADS must be the https:// Media Library folder, ending in /.")
        recap_uploads = os.environ.get("HACKATHON_RECAP_UPLOADS", uploads)

    scripts = [config] + [read(n) for n in ("team.js", "app.js", "mentor.js")]
    out = [
        f'<link rel="stylesheet" href="{FONTS}">\n<style>\n',
        read("styles.css").strip(), "\n\n\n", read("wordpress/host.css").strip(),
        '\n\n</style>\n<div id="hackathon-page">\n', body.strip(), "\n</div>\n",
    ]
    for i, js in enumerate(scripts):
        out.append("<script>\n" if i == 0 else "\n\n</script>\n<script>\n")
        out.append(js.strip())
    out.append("\n\n</script>")
    page = "".join(out)

    # Every picture the page points at must exist, or the upload list is incomplete.
    missing = sorted({m for m in re.findall(r"assets/([\w./-]+\.(?:jpe?g|png|gif|webp))", page)
                      if not (SITE / "assets" / m).exists()})
    if missing:
        raise SystemExit("error: referenced but not in website/assets/: " + ", ".join(missing))
    # recap/ first: the general rule below would otherwise claim it.
    return page.replace("assets/recap/", recap_uploads).replace("assets/", uploads)


def main():
    built = build("--preview" in sys.argv)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(built, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(built):,} bytes)")


if __name__ == "__main__":
    main()
