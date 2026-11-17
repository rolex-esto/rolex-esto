"""Unit tests for scripts/generate-github-stats.py (standard library only).

Run from the repository root:  python3 -m unittest discover -s tests -p "test_*.py"
"""
import datetime as dt
import importlib.util
import os
import sys
import tempfile
import unittest
import xml.dom.minidom
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("stats", ROOT / "scripts" / "generate-github-stats.py")
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


def make_user(counts, stars=(3, 4), has_next=False, start=dt.date(2025, 11, 16)):
    days = []
    for i, c in enumerate(counts):
        d = start + dt.timedelta(days=i)
        lvl = "NONE" if c == 0 else "FOURTH_QUARTILE" if c >= 10 else "FIRST_QUARTILE"
        days.append({"date": d.isoformat(), "weekday": (d.weekday() + 1) % 7, "contributionCount": c, "contributionLevel": lvl})
    weeks, cur = [], []
    for d in days:
        if cur and d["weekday"] == 0:
            weeks.append({"contributionDays": cur}); cur = []
        cur.append(d)
    weeks.append({"contributionDays": cur})
    return {
        "login": "octo", "name": "Octo Cat", "createdAt": "2024-11-17T00:00:00Z", "avatarUrl": "https://example.invalid/a.png",
        "followers": {"totalCount": 2}, "publicRepos": {"totalCount": 5},
        "contributionsCollection": {
            "totalCommitContributions": 10, "totalPullRequestContributions": 2, "totalIssueContributions": 1,
            "totalRepositoriesWithContributedCommits": 3, "restrictedContributionsCount": 4,
            "contributionCalendar": {"totalContributions": sum(counts), "weeks": weeks}},
        "repositories": {"totalCount": len(stars), "pageInfo": {"hasNextPage": has_next, "endCursor": "c1"},
                         "nodes": [{"stargazerCount": s, "languages": {"edges": [
                             {"size": 100, "node": {"name": "Python", "color": "#3572A5"}}]}} for s in stars]},
    }


class Streaks(unittest.TestCase):
    def test_today_zero_does_not_break_current_streak(self):
        days = [{"contributionCount": c} for c in [1, 0, 2, 3, 4, 0]]
        self.assertEqual(stats.streaks(days), (3, 3))

    def test_longest_inside_window(self):
        days = [{"contributionCount": c} for c in [1, 1, 1, 1, 0, 1, 1]]
        self.assertEqual(stats.streaks(days), (2, 4))

    def test_all_zero(self):
        self.assertEqual(stats.streaks([{"contributionCount": 0}] * 10), (0, 0))


class Summarize(unittest.TestCase):
    def test_totals_and_window(self):
        s = stats.summarize(make_user([1] * 367, stars=(3, 4)))
        self.assertEqual((s["stars"], s["followers"], s["public_repos"], s["issues"]), (7, 2, 5, 1))
        self.assertEqual((s["start"], s["end"]), ("2025-11-16", "2026-11-17"))
        self.assertEqual(len(s["days"]), 367)

    def test_incomplete_calendar_rejected(self):
        with self.assertRaises(stats.StatsError):
            stats.summarize(make_user([1] * 100))

    def test_missing_number_rejected(self):
        u = make_user([1] * 367)
        u["followers"] = None
        with self.assertRaises(stats.StatsError):
            stats.summarize(u)


class Pagination(unittest.TestCase):
    def test_stars_summed_across_pages(self):
        pages = [make_user([1] * 367, stars=(1, 2), has_next=True), make_user([1] * 367, stars=(5,), has_next=False)]
        calls = []

        def fake(login, token, after=None):
            calls.append(after)
            return pages[len(calls) - 1]
        u = stats.fetch_all("octo", "t", fetch_page=fake)
        self.assertEqual(calls, [None, "c1"])
        self.assertEqual(stats.summarize(u)["stars"], 8)


class Overview(unittest.TestCase):
    def render(self, counts, avatar=None):
        s = stats.summarize(make_user(counts))
        return s, {m: stats.overview_card(s, stats.DASH[m], avatar) for m in stats.DASH}

    def test_valid_xml_both_themes_with_one_cell_per_day(self):
        _, out = self.render([i % 7 for i in range(367)])
        for svg in out.values():
            xml.dom.minidom.parseString(svg)
            self.assertEqual(svg.count('rx="1" fill='), 367)

    def test_empty_year_renders_flat_graph(self):
        _, out = self.render([0] * 367)
        self.assertIn("no contributions yet", out["dark"])
        xml.dom.minidom.parseString(out["dark"])

    def test_block_height_follows_real_counts(self):
        s, _ = self.render([0] * 360 + [1, 2, 4, 8, 16, 32, 64])
        _, peak = stats.isometric(s["days"], stats.DASH["dark"], 50, 50)
        self.assertEqual(peak, 64)

    def test_initials_when_avatar_missing(self):
        _, out = self.render([1] * 367, avatar=None)
        self.assertIn(">OC</text>", out["dark"])
        self.assertNotIn("<image", out["dark"])

    def test_labels_state_period_and_private_counts(self):
        _, out = self.render([1] * 367)
        self.assertIn("Nov 16, 2025 – Nov 17, 2026", out["dark"])
        self.assertIn("includes private contribution counts", out["dark"])


class FailureKeepsPreviousImages(unittest.TestCase):
    def test_api_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d, "overview-activity-dark.svg")
            old.write_text("<svg>previous</svg>")
            with mock.patch.object(stats, "fetch", side_effect=stats.StatsError("boom")), \
                 mock.patch.dict(os.environ, {"GITHUB_TOKEN": "x"}), \
                 mock.patch.object(sys, "argv", ["x", "octo", d]):
                with self.assertRaises(SystemExit) as e:
                    stats.main()
            self.assertEqual(e.exception.code, 1)
            self.assertEqual(old.read_text(), "<svg>previous</svg>")
            self.assertEqual(sorted(os.listdir(d)), ["overview-activity-dark.svg"])

    def test_success_writes_all_six_files(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(stats, "fetch", return_value=make_user([1] * 367)), \
                 mock.patch.object(stats, "fetch_avatar", return_value=None), \
                 mock.patch.dict(os.environ, {"GITHUB_TOKEN": "x"}), \
                 mock.patch.object(sys, "argv", ["x", "octo", d]), \
                 mock.patch("builtins.print"):
                stats.main()
            self.assertEqual(len(os.listdir(d)), 6)


if __name__ == "__main__":
    unittest.main()
