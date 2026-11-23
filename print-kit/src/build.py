"""Build every print file from the CSV lists in sample-data/print-kit.

    python print-kit/src/build.py

The lists are checked first. If a row is wrong (an unknown role, a winner without a team), nothing is
built and the message names the file and line. Set PRINT_KIT_DATA to use your own lists.
Output goes to output/print-kit/.
"""
import csv
import io
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = Path(os.environ.get("PRINT_KIT_DATA", ROOT / "sample-data" / "print-kit"))
sys.path.insert(0, str(HERE))

import lanyard          # noqa: E402
import team_stickers    # noqa: E402
import certificates     # noqa: E402
import badge_back       # noqa: E402
import signs            # noqa: E402
import team_desk        # noqa: E402
import pattern          # noqa: E402
import team_number_stickers  # noqa: E402
import team_list        # noqa: E402
from reportlab.lib.pagesizes import A4 as _A4, A3 as _A3

PRINTER_SCALE = 1.036   # the Example College printer shrinks pages to about 96%; this cancels it

ROLES = list(lanyard.ROLES)                       # PARTICIPANT, MENTOR, ...
TYPES = ["participation", "winner", "audience", "mentor", "staff", "staff lead"]
AWARDS = ["winner", "audience"]
problems = []


def read_list(name, required):
    path = DATA / name
    if not path.exists():
        problems.append(f"{name}: file not found in the data folder")
        return []
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "mac_roman"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    first_line = text.splitlines()[0] if text.strip() else ""
    delim = ";" if first_line.count(";") > first_line.count(",") else ("\t" if "\t" in first_line else ",")
    rows = []
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    headers = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = [h for h in required if h not in headers]
    if missing:
        problems.append(f"{name}: missing column(s) {', '.join(missing)} (first row must be: {', '.join(required)})")
        return []
    for n, row in enumerate(reader, start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        if not any(row.values()):
            continue
        if next(iter(row.values()), "").startswith("#"):     # hint rows are ignored
            continue
        row["_line"] = n
        rows.append(row)
    return rows


def main():
    out = ROOT / "output" / "print-kit"
    out.mkdir(parents=True, exist_ok=True)

    # ---- badges
    badges = read_list("badges.csv", ["first", "last", "role"])
    for r in badges:
        r["role"] = r["role"].upper()
        if r["role"] not in ROLES:
            problems.append(f"badges.csv line {r['_line']}: role '{r['role']}' is not one of {', '.join(ROLES)}")

    # ---- team stickers
    stickers = []
    for r in read_list("teams.csv", ["team", "copies"]):
        try:
            n = int(r["copies"] or 1)
        except ValueError:
            problems.append(f"teams.csv line {r['_line']}: copies '{r['copies']}' is not a number")
            continue
        stickers += [r["team"]] * n

    # ---- certificates
    certs = read_list("certificates.csv", ["type", "first", "last", "team", "product"])
    for r in certs:
        r["type"] = r["type"].lower()
        if r["type"] not in TYPES:
            problems.append(f"certificates.csv line {r['_line']}: type '{r['type']}' is not one of {', '.join(TYPES)}")
        if r["type"] in AWARDS and not r["team"]:
            problems.append(f"certificates.csv line {r['_line']}: a {r['type']} certificate needs a team")

    # ---- awards: winner / audience award for a whole team, names taken from the participation rows
    def team_key(s):
        s = (s or "").strip().lower()
        return s[5:].strip() if s.startswith("team ") else s
    award_certs = []
    awards_path = DATA / "awards.csv"
    for r in (read_list("awards.csv", ["award", "team"]) if awards_path.exists() else []):
        award = r["award"].lower()
        if award not in AWARDS:
            problems.append(f"awards.csv line {r['_line']}: award '{r['award']}' is not one of {', '.join(AWARDS)}")
            continue
        members = [p for p in certs if p["type"] == "participation" and team_key(p["team"]) == team_key(r["team"])]
        if not members:
            problems.append(f"awards.csv line {r['_line']}: no participation rows for team '{r['team']}' "
                            f"in certificates.csv")
        for p in members:
            award_certs.append(dict(type=award, first=p["first"], last=p["last"], team=p["team"],
                                    product=r.get("product") or p["product"]))

    # ---- team list (who is in which team)
    roster = read_list("team_list.csv", ["team", "name", "role"])
    for r in roster:
        if r["team"] not in [n for n, _ in team_desk.TEAMS]:
            problems.append(f"team_list.csv line {r['_line']}: team '{r['team']}' should be 1, 2, 3 or 4")
        if r["role"].lower() not in ("mentor", "participant"):
            problems.append(f"team_list.csv line {r['_line']}: role '{r['role']}' should be Mentor or Participant")

    if problems:
        print("\nNothing was built. Please fix these first:\n")
        for p in problems:
            print("  -", p)
        print()
        sys.exit(1)

    for f in out.glob("*.pdf"):            # only the files this build makes (they start with a number)
        if re.match(r"\d+b?-", f.name):
            f.unlink()
    made = []
    if badges:
        lanyard.make(badges, str(out / "1-badges-A6-PRINT-THIS.pdf"), PRINTER_SCALE)
        lanyard.make(badges, str(out / "1-badges-A6-true-size-100-percent.pdf"), 1.0)
        badge_back.make(str(out / "1b-badge-BACKS-PRINT-THIS.pdf"), PRINTER_SCALE)
        badge_back.make(str(out / "1b-badge-BACKS-true-size-100-percent.pdf"), 1.0)
        made.append(f"{len(badges)} badges")
    if stickers:
        team_stickers.make(stickers, str(out / "2-team-stickers-CHECK-on-plain-paper-first.pdf"), PRINTER_SCALE, check=True)
        team_stickers.make(stickers, str(out / "2-team-stickers-PRINT-THIS.pdf"), PRINTER_SCALE)
        team_stickers.make(stickers, str(out / "2-team-stickers-true-size-100-percent.pdf"), 1.0)
        made.append(f"{len(stickers)} team stickers")
    # A team with an award gets the award certificate INSTEAD of the participation one.
    awarded = {team_key(r["team"]) for r in award_certs}
    all_certs = certs
    certs = [r for r in certs if not (r["type"] == "participation" and team_key(r["team"]) in awarded)]
    if certs:
        certificates.make(certs, str(out / "3-certificates.pdf"))
        made.append(f"{len(certs)} certificates")
    if award_certs:
        certificates.make(award_certs, str(out / "3b-award-certificates.pdf"))
        made.append(f"{len(award_certs)} award certificates")

    # awards-ready: winner and audience-award certificates for every team, ready before the judging ends
    ready = out / "awards-ready"
    ready.mkdir(exist_ok=True)
    for f in ready.glob("*.pdf"):
        f.unlink()
    teams = {}
    for p in all_certs:
        if p["type"] == "participation" and p["team"]:
            teams.setdefault(team_key(p["team"]), []).append(p)
    for key in sorted(teams):
        members = teams[key]
        product = members[0]["product"]
        name = f"Team-{key}" if key.isdigit() else key.title().replace(" ", "-")
        if product:
            name += "-" + re.sub(r"[^A-Za-z0-9]+", "-", product).strip("-")
        for award, label in (("winner", "WINNER"), ("audience", "AUDIENCE-AWARD")):
            certificates.make([dict(p, type=award) for p in members], str(ready / f"{label}-{name}.pdf"))
    if teams:
        made.append(f"award certificates ready for all {len(teams)} teams (output/awards-ready)")
    team_number_stickers.make(str(out / "2b-team-NUMBER-stickers-PRINT-THIS.pdf"), PRINTER_SCALE)
    team_number_stickers.make(str(out / "2b-team-NUMBER-stickers-true-size-100-percent.pdf"), 1.0)
    made.append("40 team number stickers")
    if roster:
        team_list.make(roster, str(out / "7-team-list-A4.pdf"))
        made.append("team list (2 pages)")
    signs.make(str(out / "4-direction-signs-A4.pdf"), _A4)
    signs.make(str(out / "4-direction-signs-A3.pdf"), _A3)
    made.append("5 direction signs (A4 + A3)")
    team_desk.make(str(out / "5-team-desk-signs-A4.pdf"))
    team_desk.make_flat(str(out / "5-team-desk-signs-flat-A4.pdf"))
    team_desk.make_portrait(str(out / "5-team-desk-signs-upright-A4.pdf"))
    made.append("4 team desk signs")
    pattern.make(str(out / "6-pattern-page-A4.pdf"))
    made.append("1 pattern page")
    print("\nDone: " + ", ".join(made) + ".\nThe PDFs are in output/print-kit.\n")


if __name__ == "__main__":
    main()
