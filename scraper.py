"""Scholarly paper search via free APIs — no key, no browser, no CAPTCHA.

Primary source: Semantic Scholar API (titles, authors, year, citation counts,
abstracts). Fallback: OpenAlex (very generous rate limits).

Returns (papers, status) where status is one of:
  "ok"      — papers found
  "blocked" — services temporarily unavailable (rate limit / network)
  "empty"   — search worked but no results found
"""

import json
import urllib.parse
import urllib.request

_UA = {"User-Agent": "ResearchDashboard/1.0 (mailto:rajpootkashi702@gmail.com)"}


def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError("HTTP {}".format(resp.status))
        return json.loads(resp.read().decode("utf-8"))


def _fmt_authors(names, year):
    if not names:
        auth = "Unknown"
    elif len(names) == 1:
        auth = names[0]
    elif len(names) == 2:
        auth = "{} & {}".format(names[0], names[1])
    else:
        auth = "{} et al.".format(names[0])
    return "{} - {}".format(auth, year) if year else auth


# ---------------- Semantic Scholar (primary) ----------------

def _from_semantic_scholar(query, max_results):
    params = urllib.parse.urlencode({
        "query": query,
        "limit": max_results,
        "fields": "title,authors,year,citationCount,abstract,url,openAccessPdf",
    })
    data = _get_json(
        "https://api.semanticscholar.org/graph/v1/paper/search?" + params)
    papers = []
    for index, item in enumerate(data.get("data") or []):
        title = (item.get("title") or "").strip()
        if not title:
            continue
        names = [a.get("name", "") for a in (item.get("authors") or [])
                 if a.get("name")]
        pdf = item.get("openAccessPdf") or {}
        papers.append({
            "Rank": index + 1,
            "Title": title,
            "Authors_and_Year": _fmt_authors(names, item.get("year")),
            "Citations": str(item.get("citationCount") or 0),
            "Link": pdf.get("url") or item.get("url") or "",
            "Abstract_Snippet": (item.get("abstract") or
                                 "No abstract available.").strip(),
        })
    return papers


# ---------------- OpenAlex (fallback) ----------------

def _reconstruct_abstract(inv_index):
    if not inv_index:
        return "No abstract available."
    positions = {}
    for word, idx_list in inv_index.items():
        for i in idx_list:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def _from_openalex(query, max_results):
    params = urllib.parse.urlencode({
        "search": query,
        "per-page": max_results,
        "mailto": "rajpootkashi702@gmail.com",
    })
    data = _get_json("https://api.openalex.org/works?" + params)
    papers = []
    for index, item in enumerate(data.get("results") or []):
        title = (item.get("title") or "").strip()
        if not title:
            continue
        names = []
        for a in (item.get("authorships") or [])[:3]:
            author = a.get("author") or {}
            if author.get("display_name"):
                names.append(author["display_name"])
        doi = item.get("doi")
        loc = item.get("primary_location") or {}
        papers.append({
            "Rank": index + 1,
            "Title": title,
            "Authors_and_Year": _fmt_authors(
                names, item.get("publication_year")),
            "Citations": str(item.get("cited_by_count") or 0),
            "Link": ("https://doi.org/" + doi.lstrip("https://doi.org/")
                     if doi else loc.get("landing_page_url") or ""),
            "Abstract_Snippet": _reconstruct_abstract(
                item.get("abstract_inverted_index")),
        })
    return papers


# ---------------- public entry point ----------------

def scrape_scholar(query, max_results=5, headless=True, timeout_ms=12000):
    """Kept the historic name so app.py needs no import changes."""
    for source_fn in (_from_semantic_scholar, _from_openalex):
        try:
            papers = source_fn(query, max_results)
        except Exception:
            continue  # try the next source
        if papers:
            return papers, "ok"
        return [], "empty"  # source worked, just no results
    return [], "blocked"
