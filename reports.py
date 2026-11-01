"""Pure report-generation helpers (no Streamlit/Playwright imports) — easy to test."""
import csv
import io
import json
import re


def clean_filename(text):
    """Creates a safe filename from a string."""
    name = "".join(c if c.isalnum() else "_" for c in str(text)).lower()[:30]
    return name or "research"


def parse_citations(value):
    """Turns '1,234' / 'Cited by 56' / 0 into an int."""
    try:
        return int(re.sub(r"[^\d]", "", str(value)) or 0)
    except (ValueError, TypeError):
        return 0


def to_json_str(papers):
    return json.dumps(papers, indent=4, ensure_ascii=False)


def to_csv_str(papers):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(papers[0].keys()))
    writer.writeheader()
    writer.writerows(papers)
    return "\ufeff" + buf.getvalue()  # BOM so Excel opens UTF-8 correctly


def to_markdown(papers, query):
    lines = ["# Research Report: {}".format(str(query).strip().title()), ""]
    for p in papers:
        lines.append("### {}. {}".format(p["Rank"], p["Title"]))
        lines.append("**Authors/Year:** {} | **Citations:** {}".format(
            p["Authors_and_Year"], p["Citations"]))
        lines.append("")
        lines.append("> {}".format(p["Abstract_Snippet"]))
        lines.append("")
        lines.append("[Source Link]({})".format(p["Link"]))
        lines.append("---")
    return "\n".join(lines)
