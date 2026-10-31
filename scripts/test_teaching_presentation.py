from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TeachingPresentationTests(unittest.TestCase):
    def test_comments_precede_evaluation_figure(self):
        page = (ROOT / "content/teaching/_index.md").read_text(encoding="utf-8")
        self.assertLess(page.index("### Selected Student Comments"),
                        page.index("### Teaching Evaluations"))
        self.assertEqual(page.count("{{< teaching-evaluations >}}"), 1)
        self.assertEqual(page.count('class="student-comment-source"'), 6)

    def test_figure_shows_personal_scores_for_every_group(self):
        template = (ROOT / "layouts/shortcodes/teaching-evaluations.html").read_text(encoding="utf-8")
        self.assertIn('<figure class="teaching-evaluations"', template)
        self.assertIn("range site.Data.teaching_evaluations.groups", template)
        self.assertIn("range .rows", template)
        self.assertIn('{{ .personal }}</span>', template)
        self.assertIn('{{ $group.title }} - {{ .label }}: {{ .personal }} out of 5', template)
        for removed in ("School/college", "University</span>", "evaluation-legend", '"college"', '"university"'):
            self.assertNotIn(removed, template)

    def test_shared_scale_and_method_remain_explicit(self):
        template = (ROOT / "layouts/shortcodes/teaching-evaluations.html").read_text(encoding="utf-8")
        self.assertIn("Average Course Median (out of 5)", template)
        self.assertIn("mul (float .personal) 20", template)
        self.assertIn("{{ .coverage }}", template)
        for tick in range(6):
            self.assertIn(f"<span>{tick}</span>", template)
        self.assertIn("unweighted averages of the medians", template)


if __name__ == "__main__":
    unittest.main()
