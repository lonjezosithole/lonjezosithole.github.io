from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HomepagePresentationTests(unittest.TestCase):
    def setUp(self):
        self.css = (ROOT / "layouts/partials/hooks/head-end/site-polish.html").read_text()

    def test_bio_keeps_soft_white_and_existing_type_size(self):
        rule = re.search(r"\.bio-text p\s*\{([^}]+)\}", self.css).group(1)
        self.assertIn("color: #e5e9ef;", rule)
        self.assertIn("font-size: 1.05rem;", rule)
        self.assertIn("line-height: 1.75;", rule)
        self.assertNotIn("font-weight:", rule)

    def test_justification_is_limited_to_desktop_intro(self):
        rule = re.search(
            r"@media \(min-width: 1024px\)\s*\{\s*"
            r"#section-resume-biography-3 \.bio-text p:first-child\s*\{([^}]+)\}",
            self.css,
        ).group(1)
        self.assertIn("text-align: justify;", rule)
        self.assertIn("text-align-last: left;", rule)
        self.assertEqual(self.css.count("text-align: justify;"), 1)
        self.assertNotIn("font-weight:", rule)


if __name__ == "__main__":
    unittest.main()
