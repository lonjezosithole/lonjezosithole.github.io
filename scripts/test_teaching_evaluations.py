from decimal import Decimal
import json
from pathlib import Path
import unittest

from build_teaching_evaluations import parse_table, QUESTIONS, SERIES, summarize


def sample_table(reverse_benchmarks=False):
    benchmarks = ["School/College\nMedian", "Univ-wide\nMedian"]
    medians = ["4.6", "4.7"]
    if reverse_benchmarks:
        benchmarks.reverse()
        medians.reverse()
    header = ["", "SA", "A", "N", "D", "SD", "N/A", "Your\nMedian", *benchmarks]
    rows = [[f"Lonjezo Sithole {label} ({question})", "8", "2", "0", "0", "0", "0", "4.9", *medians]
            for question, label in QUESTIONS.items()]
    return [header, *rows]


class TeachingEvaluationTests(unittest.TestCase):
    def test_reordered_benchmark_columns(self):
        self.assertEqual(parse_table(sample_table()), parse_table(sample_table(True)))

    def test_wrapped_pdf_cells(self):
        table = sample_table()
        row = table[1]
        table[1] = ["\n".join(row), *([None] * 9)]
        self.assertEqual(parse_table(table), parse_table(sample_table()))

    def test_rejects_missing_item(self):
        with self.assertRaises(ValueError):
            parse_table(sample_table()[:-1])

    def test_rejects_wrong_instructor(self):
        table = sample_table()
        table[1][0] = table[1][0].replace("Lonjezo Sithole", "Another instructor")
        with self.assertRaises(ValueError):
            parse_table(table)

    def test_rejects_invalid_median(self):
        table = sample_table()
        table[1][7] = "6.0"
        with self.assertRaises(ValueError):
            parse_table(table)

    def test_equal_section_weighting_and_rounding(self):
        values = parse_table(sample_table())
        changed = {question: dict(scores, personal=Decimal("4.8")) for question, scores in values.items()}
        reports = [{"course": "503", "year": "2023", "term": "FA", "values": scores}
                   for scores in [values, values, values, changed]]
        rows = summarize(reports)["groups"][0]["rows"]
        self.assertTrue(all(row["personal"] == "4.88" for row in rows))
        self.assertTrue(all(row["college"] == "4.60" for row in rows))

    def test_saved_chart_data(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "data/teaching_evaluations.json").read_text())
        self.assertEqual([group["id"] for group in data["groups"]], ["phd", "masters", "undergraduate"])
        for group in data["groups"]:
            self.assertEqual([row["question"] for row in group["rows"]], list(QUESTIONS))
            for row in group["rows"]:
                for series in SERIES:
                    self.assertTrue(1 <= Decimal(row[series]) <= 5)
        research = (root / "content/research.md").read_text(encoding="utf-8")
        paper_links = {
            "Multimargin Selection in Leniency Designs (Job Market Paper)":
                "https://lsa.umich.edu/econ/news-events/all-events.detail.html/151819-21912225.html",
            "A Locally Robust Semiparametric Approach to Examiner IV Designs":
                "https://arxiv.org/abs/2404.19144",
            "Nonparametric Testability of Slutsky Symmetry":
                "https://arxiv.org/abs/2505.05603",
        }
        for title, url in paper_links.items():
            self.assertIn(f"> #### [{title}]({url}", research)
        for anchor in ["multi-margin-selection-in-leniency-designs",
                       "a-locally-robust-semiparametric-approach-to-examiner-iv-designs",
                       "nonparametric-testability-of-slutsky-symmetry"]:
            self.assertIn(f"{{#{anchor}}}", research)
        self.assertNotIn("**Status:** Job Market Paper", research)
        self.assertNotIn("**Links:**", research)
        self.assertEqual(research.count("**Status:** Draft Coming"), 2)
        self.assertNotIn("New Draft Coming", research)
        self.assertIn("151819-21912225.html", research)
        self.assertEqual(research.count('<details class="paper-abstract">'), 2)


if __name__ == "__main__":
    unittest.main()
