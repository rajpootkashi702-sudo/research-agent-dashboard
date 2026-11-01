"""Google Scholar scraper (Playwright).

Returns (papers, status) where status is one of:
  "ok"      — papers extracted
  "blocked" — Scholar showed a CAPTCHA / bot check, or no browser available
  "empty"   — page loaded but no results found
"""

import os
import subprocess


def _ensure_chromium(timeout_s=600):
    """Install Playwright's Chromium at runtime if it is missing.

    Streamlit Cloud does not ship browser binaries, so on the first search
    we install Chromium once into ~/.cache/ms-playwright. Returns True when
    a usable Chromium is available.
    """
    cache = os.path.expanduser("~/.cache/ms-playwright")
    try:
        if os.path.isdir(cache) and any("chromium" in d.lower()
                                        for d in os.listdir(cache)):
            return True
    except OSError:
        pass
    try:
        subprocess.run(["playwright", "install", "chromium"],
                       check=True, capture_output=True, timeout=timeout_s)
        return True
    except Exception:
        return False


def scrape_scholar(query, max_results=5, headless=True, timeout_ms=12000):
    from playwright.sync_api import sync_playwright

    if not _ensure_chromium():
        return [], "blocked"

    papers = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            try:
                page.goto("https://scholar.google.com/", timeout=30000)
                page.fill("input[name='q']", query)
                page.press("input[name='q']", "Enter")
                page.wait_for_selector(".gs_r.gs_or.gs_scl", timeout=timeout_ms)
            except Exception:
                browser.close()
                return [], "blocked"

            rows = page.query_selector_all(".gs_r.gs_or.gs_scl")
            for index, row in enumerate(rows[:max_results]):
                title_el = row.query_selector(".gs_rt a")
                if not title_el:
                    continue
                abstract_el = row.query_selector(".gs_rs")
                meta_el = row.query_selector(".gs_a")
                cite_el = row.query_selector("a:has-text('Cited by')")
                papers.append({
                    "Rank": index + 1,
                    "Title": title_el.inner_text().strip(),
                    "Authors_and_Year": meta_el.inner_text().strip() if meta_el else "Unknown",
                    "Citations": (cite_el.inner_text().replace("Cited by", "").strip()
                                  if cite_el else "0"),
                    "Link": title_el.get_attribute("href") or "",
                    "Abstract_Snippet": (abstract_el.inner_text().replace("\n", " ").strip()
                                         if abstract_el else "No abstract available."),
                })
            browser.close()
    except Exception:
        return [], "blocked"

    if not papers:
        return [], "empty"
    return papers, "ok"
