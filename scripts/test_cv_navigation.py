from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CVNavigationTests(unittest.TestCase):
    def test_cv_uses_one_existing_pdf_for_preview_and_links(self):
        page = (ROOT / "content/cv.md").read_text(encoding="utf-8")
        self.assertIn("layout: cv", page)
        pdf = re.search(r"^cv_pdf: (.+)$", page, re.MULTILINE).group(1)
        self.assertTrue((ROOT / "static" / pdf.lstrip("/")).is_file())
        template = (ROOT / "layouts/_default/cv.html").read_text(encoding="utf-8")
        self.assertIn(".Params.cv_pdf | relURL", template)
        self.assertEqual(template.count('href="{{ $pdf }}"'), 2)
        self.assertIn('src="{{ $pdf }}#view=FitH', template)
        self.assertIn('title="Lonjezo Sithole\'s curriculum vitae"', template)
        self.assertIn('download>Download CV (PDF)', template)
        self.assertIn('target="_blank" rel="noopener"', template)

    def test_contact_removed_from_menu_but_page_preserved(self):
        menu = (ROOT / "config/_default/menus.yaml").read_text(encoding="utf-8")
        self.assertNotIn("name: Contact", menu)
        self.assertNotIn("url: contact/", menu)
        self.assertIn("name: CV", menu)
        self.assertTrue((ROOT / "content/contact.md").is_file())

    def test_email_profile_follows_linkedin_and_has_accessible_label(self):
        profile = (ROOT / "content/authors/admin/_index.md").read_text(encoding="utf-8")
        profiles = profile.split("profiles:\n", 1)[1].split("\ninterests:", 1)[0]
        self.assertLess(profiles.index("brands/linkedin"), profiles.index("envelope"))
        self.assertIn("url: mailto:lsithole@umich.edu", profiles)
        self.assertIn("label: Email lsithole@umich.edu", profiles)
        template = (ROOT / "layouts/partials/blox/resume-biography-3.html").read_text(encoding="utf-8")
        self.assertIn('aria-label="{{ .label | default .icon }}"', template)


if __name__ == "__main__":
    unittest.main()
