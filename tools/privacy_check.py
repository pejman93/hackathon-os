#!/usr/bin/env python3
"""Fail if anything that looks like real personal data or a private link is in the repository.

    python tools/privacy_check.py

Everything in this repository is meant to be fictional. This check runs in CI and looks for:
  - email addresses outside the reserved example domains
  - phone numbers other than the one fictional number
  - private links: chat invites, shared documents, deployed scripts, personal profiles
  - API keys, tokens and private keys
  - any name in a sample list that is not in sample-data/fictional-people.txt
  - metadata inside images (camera data, location, author)
"""
import csv
import pathlib
import re
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", "output"}
SKIP_FILES = {"tools/privacy_check.py", "tests/test_tools.py"}     # these two hold the patterns
TEXT = {".py", ".gs", ".js", ".html", ".css", ".md", ".txt", ".csv", ".json", ".yml", ".yaml", ".svg"}
IMAGES = {".png", ".jpg", ".jpeg", ".gif"}

EMAIL = re.compile(r"[\w.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
SAFE_EMAIL = re.compile(r".*@(example\.org|example\.com|users\.noreply\.github\.com)$", re.I)
PLACEHOLDER_EMAILS = {"you@company.com"}
PHONE = re.compile(r"(?<![\w.#-])(?:\+\d{1,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,}[\s-]?\d{0,6}|0\d{2,4}[\s/-]\d{5,})(?![\w-])")
SAFE_PHONES = {"+49 30 23125 000", "+493023125000"}
PRIVATE_LINK = re.compile(
    r"discord\.gg/\w|discord\.com/invite|docs\.google\.com/|drive\.google\.com/|forms\.gle/|"
    r"script\.google\.com/macros/s/[A-Za-z0-9_-]{20,}|calendar\.app\.google|sli\.do/|miro\.com/app|"
    r"maps\.app\.goo|youtu\.be/|youtube\.com/watch|vercel\.app|wa\.me/|tiktok\.com/@|"
    r"instagram\.com/\w|facebook\.com/\w|linkedin\.com/(?:company|in)/(?!your-name)[\w%-]+", re.I)
SECRET = re.compile(
    r"AIza[\w-]{20,}|\bsk-[A-Za-z0-9-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKfyc[\w-]{20,}|xox[bap]-[\w-]{10,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY|(?i:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"\s]{8,}")
SAMPLE_LISTS = {"print-kit/badges.csv": ("first", "last"), "print-kit/certificates.csv": ("first", "last"),
                "print-kit/team_list.csv": ("name",), "documents/roster.csv": ("first", "last")}


def files(root):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_file() and not SKIP_DIRS.intersection(rel.parts) and rel.as_posix() not in SKIP_FILES:
            yield path, rel.as_posix()


def check_text(rel, text):
    found = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in EMAIL.finditer(line):
            if not SAFE_EMAIL.match(m.group(0)) and m.group(0).lower() not in PLACEHOLDER_EMAILS:
                found.append(f"{rel}:{line_no}: email address {m.group(0)}")
        for m in PHONE.finditer(line):
            if m.group(0).strip() not in SAFE_PHONES:
                found.append(f"{rel}:{line_no}: phone number {m.group(0)}")
        for m in PRIVATE_LINK.finditer(line):
            found.append(f"{rel}:{line_no}: private link {m.group(0)}")
        if SECRET.search(line):
            found.append(f"{rel}:{line_no}: possible secret")
    return found


def check_image(path, rel):
    with Image.open(path) as im:
        keys = {"comment", "Author", "Description", "Comment", "XML:com.adobe.xmp", "exif"} & set(im.info)
        if keys or len(im.getexif()):
            return [f"{rel}: image metadata ({', '.join(sorted(keys)) or 'EXIF'})"]
    return []


def check_sample_names(root):
    allowed_file = root / "sample-data" / "fictional-people.txt"
    if not allowed_file.exists():
        return []
    allowed = {l.strip() for l in allowed_file.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}
    found = []
    for name, columns in SAMPLE_LISTS.items():
        path = root / "sample-data" / name
        if not path.exists():
            continue
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.lstrip('"').startswith("#")]
        for row in csv.DictReader(lines):
            for column in columns:
                value = (row.get(column) or "").strip()
                if value and value not in allowed:
                    found.append(f"sample-data/{name}: '{value}' is not in fictional-people.txt")
    return found


def check(root=ROOT):
    root = pathlib.Path(root)
    found = check_sample_names(root)
    for path, rel in files(root):
        suffix = path.suffix.lower()
        if suffix in TEXT:
            found += check_text(rel, path.read_text(encoding="utf-8", errors="replace"))
        elif suffix in IMAGES:
            found += check_image(path, rel)
    return found


def main():
    found = check()
    for item in found:
        print(item)
    if found:
        print(f"\nFAILED: {len(found)} finding(s).")
        return 1
    print("Privacy check passed: no personal data or private links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
