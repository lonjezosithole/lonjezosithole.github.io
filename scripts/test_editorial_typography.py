from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class EditorialTypographyTests(unittest.TestCase):
    def setUp(self):
        self.css = (ROOT / "layouts/partials/editorial-style.html").read_text()

    def test_body_font_is_scoped_to_non_home_page_content(self):
        self.assertIn(
            '--site-body-font: "Source Sans 3", "Inter var", sans-serif;', self.css
        )
        rule = re.search(
            r"\{\{ if not \.IsHome \}\}\s*\.page-body\s*\{([^}]+)\}\s*\{\{ end \}\}",
            self.css,
        ).group(1)
        self.assertEqual(rule.strip(), "font-family: var(--site-body-font);")
        self.assertNotRegex(self.css, r"(?<![\w.-])body\s*\{")

    def test_headings_still_use_georgia(self):
        self.assertIn('--site-heading-font: Georgia, "Times New Roman", serif;', self.css)
        rule = re.search(
            r"\.page-body h1,\s*\.prose h2,\s*\.prose h3,\s*\.prose h4\s*\{([^}]+)\}",
            self.css,
        ).group(1)
        self.assertIn("font-family: var(--site-heading-font);", rule)
        self.assertIn("font-weight: 600;", rule)

    def test_student_comments_and_attributions_use_body_font(self):
        for selector in (r"\.prose blockquote p", r"\.prose blockquote \.student-comment-source"):
            rule = re.search(selector + r"\s*\{([^}]+)\}", self.css).group(1)
            self.assertIn("font-family: var(--site-body-font);", rule)

    def test_navigation_keeps_its_existing_font(self):
        rule = re.search(r"\.nav-link\s*\{([^}]+)\}", self.css).group(1)
        self.assertNotIn("font-family:", rule)
        self.assertNotIn("font-size:", rule)
        brand = re.search(r"\.navbar-brand\s*\{([^}]+)\}", self.css).group(1)
        self.assertIn("font-family: var(--site-heading-font);", brand)

    def test_main_reading_text_uses_slightly_larger_shared_size(self):
        self.assertIn("--site-body-size: 1.125rem;", self.css)
        rule = re.search(r"\.prose p,\s*\.prose li\s*\{([^}]+)\}", self.css).group(1)
        self.assertIn("font-size: var(--site-body-size);", rule)
        self.assertIn("line-height: 1.75;", rule)
        cv_css = (ROOT / "layouts/partials/cv-style.html").read_text()
        cv_rule = re.search(r"\.cv-actions a\s*\{([^}]+)\}", cv_css).group(1)
        self.assertIn("font-size: var(--site-body-size);", cv_rule)

    def test_quotes_and_supporting_labels_keep_existing_sizes(self):
        quote = re.search(r"\.prose blockquote p\s*\{([^}]+)\}", self.css).group(1)
        self.assertIn("font-size: 1.125rem;", quote)
        attribution = re.search(
            r"\.prose blockquote \.student-comment-source\s*\{([^}]+)\}", self.css
        ).group(1)
        self.assertIn("font-size: 0.875rem;", attribution)


if __name__ == "__main__":
    unittest.main()
