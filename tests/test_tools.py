"""Tests for the Python tools. Run from anywhere:

    python -m unittest discover -s tests
"""
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brand"))
sys.path.insert(0, str(ROOT / "tools"))

import brand                   # noqa: E402
import privacy_check           # noqa: E402


def run(*args, env=None):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})


def module(path):
    spec = importlib.util.spec_from_file_location(pathlib.Path(path).stem + "_under_test", ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


class Brand(unittest.TestCase):
    def test_colours_are_hex_and_rgb(self):
        b = brand.load()
        self.assertRegex(b.hex("accent"), r"^#?[0-9a-fA-F]{6}$")
        self.assertEqual(len(b.rgb("accent")), 3)

    def test_every_logo_file_exists(self):
        b = brand.load()
        for name in b.data["logos"]:
            self.assertTrue(pathlib.Path(b.logo(name)).exists(), name)

    def test_an_event_can_override_one_colour(self):
        with tempfile.TemporaryDirectory() as d:
            config = pathlib.Path(d, "event.json")
            config.write_text('{"brand": {"colours": {"accent": {"hex": "#00ff00"}}}}')
            b = brand.load(str(config))
            self.assertEqual(b.hex("accent").lstrip("#").lower(), "00ff00")
            self.assertEqual(b.hex("ink"), brand.load().hex("ink"))


class PrintKitChecks(unittest.TestCase):
    def build_with(self, name, text):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(ROOT / "sample-data/print-kit", d, dirs_exist_ok=True)
            pathlib.Path(d, name).write_text(text, encoding="utf-8")
            return run("print-kit/src/build.py", env={"PRINT_KIT_DATA": d})

    def test_unknown_badge_role_stops_the_build_and_names_the_line(self):
        done = self.build_with("badges.csv", "first,last,role,organisation\nAda,Lovelace,Wizard,\n")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("badges.csv line 2", done.stdout + done.stderr)

    def test_winner_certificate_needs_a_team(self):
        done = self.build_with("certificates.csv", "type,first,last,team,product\nwinner,Ada,Lovelace,,\n")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("needs a team", done.stdout + done.stderr)


class Calendar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        done = run("documents/make_calendar.py")
        if done.returncode:
            raise RuntimeError(done.stderr)
        cls.raw = (ROOT / "output/documents/Hackathon_2026.ics").read_bytes()
        cls.text = cls.raw.decode("utf-8")

    def test_four_days_published_not_invited(self):
        self.assertEqual(self.text.count("BEGIN:VEVENT"), 4)
        self.assertIn("METHOD:PUBLISH", self.text)
        self.assertNotIn("ATTENDEE", self.text)

    def test_times_carry_the_berlin_clock_change(self):
        self.assertIn("BEGIN:VTIMEZONE", self.text)
        self.assertIn("TZID:Europe/Berlin", self.text)
        self.assertIn("DTSTART;TZID=Europe/Berlin:20261025", self.text)

    def test_lines_follow_the_calendar_format(self):
        lines = self.raw.split(b"\r\n")
        self.assertGreater(len(lines), 10)
        self.assertTrue(all(len(l) <= 75 for l in lines), "a line is longer than 75 bytes")


class Scoring(unittest.TestCase):
    def criteria(self):
        source = (ROOT / "backend/judging/Judging.gs").read_text(encoding="utf-8")
        block = source[source.index("const CRITERIA"):source.index("];", source.index("const CRITERIA"))]
        return [(n, int(w)) for n, w in re.findall(r"\['([^']+)', (\d+),", block)]

    def test_the_site_shows_the_same_weights_as_the_judging_form(self):
        html = (ROOT / "website/index.html").read_text(encoding="utf-8")
        for name, weight in self.criteria():
            self.assertRegex(html, rf"{weight}%\s*(?:<[^>]+>\s*)*{re.escape(name)}")

    def test_the_paper_score_sheet_matches_the_judging_form(self):
        sheet = (ROOT / "documents/make_score_sheet.py").read_text(encoding="utf-8")
        for name, weight in self.criteria():
            self.assertIn(name, sheet)
            self.assertRegex(sheet, rf"{re.escape(name)}'?,\s*{weight}|{re.escape(name)}\s*\({weight}%\)")


class WordPressBuild(unittest.TestCase):
    OUT = ROOT / "output/website/hackathon-elementor.html"
    LIVE = {"HACKATHON_ENDPOINT": "https://script.google.com/macros/s/TESTapplication/exec",
            "HACKATHON_SIGNUP_ENDPOINT": "https://script.google.com/macros/s/TESTsignup/exec",
            "HACKATHON_UPLOADS": "https://cms.example.org/uploads/"}

    def test_preview_keeps_the_banner_and_sends_nothing(self):
        self.assertEqual(run("website/wordpress/build.py", "--preview").returncode, 0)
        page = self.OUT.read_text(encoding="utf-8")
        self.assertIn("DESIGN PREVIEW", page)
        self.assertIn("endpoint: ''", page)

    def test_live_build_removes_the_banner_and_sets_both_endpoints(self):
        self.assertEqual(run("website/wordpress/build.py", env=self.LIVE).returncode, 0)
        page = self.OUT.read_text(encoding="utf-8")
        self.assertNotIn('<div class="preview-banner">', page)
        self.assertIn("TESTapplication", page)
        self.assertIn("TESTsignup", page)
        self.assertIn("https://cms.example.org/uploads/logo.png", page)
        run("website/wordpress/build.py", "--preview")

    def test_live_build_refuses_a_wrong_endpoint(self):
        done = run("website/wordpress/build.py", env={**self.LIVE, "HACKATHON_ENDPOINT": "https://example.org/nope"})
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("HACKATHON_ENDPOINT", done.stdout + done.stderr)


class PrivacyCheck(unittest.TestCase):
    def findings(self, name, text):
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            return privacy_check.check(d)

    def test_this_repository_is_clean(self):
        self.assertEqual(privacy_check.check(ROOT), [])

    def test_it_catches_personal_data_and_private_links(self):
        for text in ("mail me at someone@gmail.com", "call +49 30 23125 999", "https://discord.gg/abcDEF1",
                     "https://docs.google.com/spreadsheets/d/abc", "https://www.linkedin.com/in/some-person",
                     "api_key = 'abcd1234efgh5678'"):
            self.assertTrue(self.findings("notes.txt", text), text)

    def test_it_allows_the_fictional_placeholders(self):
        self.assertEqual(self.findings("notes.txt", "hello@example.org, +49 30 23125 000, linkedin.com/in/your-name"), [])

    def test_a_real_looking_name_in_a_sample_list_fails(self):
        with tempfile.TemporaryDirectory() as d:
            lists = pathlib.Path(d, "sample-data/print-kit")
            lists.mkdir(parents=True)
            pathlib.Path(d, "sample-data/fictional-people.txt").write_text("Ada\nLovelace\n", encoding="utf-8")
            (lists / "badges.csv").write_text("first,last,role\nAda,Lovelace,Mentor\nSomeone,Else,Mentor\n", encoding="utf-8")
            found = privacy_check.check(d)
            self.assertEqual(len(found), 2)
            self.assertIn("Someone", found[0])


if __name__ == "__main__":
    unittest.main()
