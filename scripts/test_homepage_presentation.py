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

    def test_source_sans_is_applied_only_to_bio_paragraphs(self):
        rule = re.search(
            r"#section-resume-biography-3 \.bio-text p\s*\{([^}]+)\}", self.css
        ).group(1)
        family = 'font-family: "Source Sans 3", "Inter var", sans-serif;'
        self.assertIn(family, rule)
        self.assertEqual(self.css.count(family), 1)
        self.assertEqual(self.css.count("font-family: var(--site-heading-font);"), 2)
        editorial = (ROOT / "layouts/partials/editorial-style.html").read_text()
        self.assertIn('--site-heading-font: Georgia, "Times New Roman", serif;', editorial)

    def test_source_sans_fonts_are_self_hosted_for_existing_weights(self):
        faces = re.findall(r"@font-face\s*\{([^}]+)\}", self.css)
        self.assertEqual(len(faces), 2)
        for weight, name in ((400, "Regular"), (600, "Semibold")):
            filename = f"SourceSans3-{name}.ttf.woff2"
            face = next(face for face in faces if filename in face)
            self.assertIn('font-family: "Source Sans 3";', face)
            self.assertIn(f"font-weight: {weight};", face)
            self.assertIn("font-display: swap;", face)
            font = ROOT / "static/fonts/source-sans-3" / filename
            self.assertEqual(font.read_bytes()[:4], b"wOF2")
        license_text = (ROOT / "static/fonts/source-sans-3/LICENSE.md").read_text()
        self.assertIn("SIL OPEN FONT LICENSE", license_text)


if __name__ == "__main__":
    unittest.main()
