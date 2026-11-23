#!/usr/bin/env python3
"""Build every tool on the fictional sample data. Results go to output/.

    python tools/build_all.py                 everything
    python tools/build_all.py documents       one part
    python tools/build_all.py --assets        redraw the sample images first

Parts: print-kit, website, documents, marketing
"""
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCUMENTS = ["make_pack", "make_pack --mentors", "make_pptx", "make_pptx --mentors", "make_guide", "make_kickoff", "make_day2",
             "make_day3", "make_monday", "make_audience_chart", "make_awards", "make_pitch_template", "make_booklet",
             "make_staff", "make_mentor_plan", "make_role_plans", "make_score_sheet", "make_calendar", "make_mentor_calendar"]
MARKETING = ["posters/make-posters", "screens/make-screens", "social/make-hero", "social/make-tv", "split/make-split",
             "instagram/make-instagram", "instagram/make-carousel-a", "email-logo/make-email-logo", "event-table/make-table-set"]
PARTS = {
    "print-kit": [["print-kit/src/build.py"]],
    "website": [["website/wordpress/build.py", "--preview"]],
    "documents": [[f"documents/{d.split()[0]}.py"] + d.split()[1:] for d in DOCUMENTS],
    "marketing": [[f"marketing/{m}.py"] for m in MARKETING] +
                 [["marketing/email-banner/make_banner.py", "marketing/email-banner/jobs/demo-night.json"]],
}


def run(args):
    start = time.time()
    done = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    label = " ".join(args)
    if done.returncode:
        print(f"FAILED  {label}\n{(done.stdout + done.stderr)[-1500:]}")
        return False
    print(f"ok      {label}  ({time.time() - start:.1f}s)")
    return True


def main():
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")] or list(PARTS)
    unknown = [w for w in wanted if w not in PARTS]
    if unknown:
        sys.exit(f"Unknown part: {', '.join(unknown)}. Parts: {', '.join(PARTS)}")
    steps = [["tools/make_demo_assets.py"]] if "--assets" in sys.argv else []
    for part in wanted:
        steps += PARTS[part]
    start = time.time()
    if not all([run(step) for step in steps]):
        return 1
    total = sum(1 for p in (ROOT / "output").rglob("*") if p.is_file() and not {"_build", "_cache"} & set(p.parts))
    print(f"\nBuilt {total} files in output/ in {time.time() - start:.0f}s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
