"""Build public chart summaries from Michigan Instructor Report PDFs.

Requires pdfplumber. Run with --reports-dir PATH; --check verifies saved data.
Only aggregate medians are written, never individual responses or comments.
"""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re


QUESTIONS = {"Q230": "Prepared for class", "Q199": "Explained material clearly", "Q217": "Treated students with respect"}
SERIES = ("personal", "college", "university")
GROUPS = (
    ("phd", "PhD Courses", {"672", "675"}),
    ("masters", "Master's Courses", {"503", "504"}),
    ("undergraduate", "Undergraduate Courses", {"251"}),
)
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "teaching_evaluations.json"


def parse_table(table):
    headers = [re.sub(r"\s+", "", cell or "").lower() for cell in table[0]]
    median_keys = []
    for header in headers[-3:]:
        if "your" in header:
            median_keys.append("personal")
        elif "school/college" in header:
            median_keys.append("college")
        elif "univ" in header:
            median_keys.append("university")
        else:
            raise ValueError(f"Unrecognized benchmark header: {header}")
    if set(median_keys) != set(SERIES):
        raise ValueError("Missing or duplicate median columns")

    values = {}
    for row in table[1:]:
        text = " ".join(cell for cell in row if cell)
        ids = re.findall(r"Q\d+", text)
        if len(ids) != 1 or ids[0] not in QUESTIONS:
            raise ValueError(f"Unexpected instructor item: {text}")
        if "Lonjezo Sithole" not in text:
            raise ValueError("Instructor item does not identify Lonjezo Sithole")
        numbers = re.findall(r"\d+(?:\.\d+)?", re.sub(r"Q\d+", "", text))
        if len(numbers) != 9:
            raise ValueError(f"Expected six counts and three medians: {text}")
        medians = [Decimal(value) for value in numbers[-3:]]
        if not all(1 <= value <= 5 for value in medians):
            raise ValueError("Median outside the five-point scale")
        if ids[0] in values:
            raise ValueError("Duplicate instructor item")
        values[ids[0]] = dict(zip(median_keys, medians))
    if set(values) != set(QUESTIONS):
        raise ValueError("Missing instructor items")
    return values


def read_reports(directory):
    import pdfplumber

    reports = []
    identities = set()
    for path in sorted(directory.glob("*Instructor Report*.pdf")):
        match = re.match(r"(FA|WN) (\d{4}) Instructor Report of ECON (\d+)-(\d+)", path.name)
        if not match:
            raise ValueError(f"Unexpected report name: {path.name}")
        term, year, course, section = match.groups()
        identity = (term, year, course, section)
        if identity in identities:
            raise ValueError(f"Duplicate section: {identity}")
        identities.add(identity)
        with pdfplumber.open(path) as document:
            tables = [table for table in document.pages[0].extract_tables()
                      if any("Q199" in (cell or "") for row in table for cell in row)]
        if len(tables) != 1:
            raise ValueError(f"Expected one instructor benchmark table: {path.name}")
        reports.append({"course": course, "term": term, "year": year, "values": parse_table(tables[0])})
    if not reports:
        raise ValueError("No Instructor Report PDFs found")
    known_courses = set.union(*(courses for _, _, courses in GROUPS))
    if any(report["course"] not in known_courses for report in reports):
        raise ValueError("Add the new course to GROUPS before generating charts")
    return reports


def summarize(reports):
    groups = []
    for key, title, courses in GROUPS:
        sections = [report for report in reports if report["course"] in courses]
        if not sections:
            continue
        offerings = sorted({(report["course"], report["year"], report["term"]) for report in sections})
        coverage = "; ".join(f"ECON {course} ({'Fall' if term == 'FA' else 'Winter'} {year})"
                             for course, year, term in offerings)
        rows = []
        for question, label in QUESTIONS.items():
            row = {"question": question, "label": label}
            for series in SERIES:
                # Match the equal-section weighting for personal and benchmark medians.
                mean = sum(report["values"][question][series] for report in sections) / len(sections)
                row[series] = str(mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            rows.append(row)
        groups.append({"id": key, "title": title, "coverage": coverage, "rows": rows})
    return {"groups": groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    reports = read_reports(args.reports_dir)
    data = summarize(reports)
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != data:
            raise SystemExit("Chart data do not match the original reports")
        print(f"PASS: All chart summaries match {len(reports)} instructor reports.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Generated {OUTPUT} from {len(reports)} instructor reports.")


if __name__ == "__main__":
    main()
