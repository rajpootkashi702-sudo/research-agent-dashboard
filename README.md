# 📚 Literature Research Dashboard

A Streamlit web dashboard for the Professional Academic Literature Research Agent.
Search Google Scholar, review the top papers with charts, and export JSON / CSV / Markdown reports.

## Run locally

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Put it on the web (free) — Streamlit Cloud

1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. New app → pick the repo, set main file to `app.py`, Deploy.
4. You get a public link like `https://your-app.streamlit.app` — share it with clients.

> Note: on Streamlit Cloud, `packages.txt` installs the system libraries Chromium
> needs, and the app installs Playwright's Chromium itself on the first search
> (~1–2 min one-time). Scholar may still show a CAPTCHA to bots —
> the dashboard has a **demo mode** so it always presents well.

## Make it an Android APK

A Streamlit app cannot compile directly to an APK (it needs a Python server).
The practical route:

1. Deploy the dashboard to Streamlit Cloud (steps above) — you now have a link.
2. Wrap that link in a WebView APK with a free tool like **AppsGeyser**,
   **WebIntoApp**, or **Median** (10 minutes, no coding) — or simply use
   Chrome's **Add to Home Screen** on the link for an app-like icon.

## Files

| File | What it does |
|------|--------------|
| `app.py` | The Streamlit dashboard (UI) |
| `scraper.py` | Google Scholar scraping with Playwright |
| `reports.py` | JSON / CSV / Markdown report builders (pure functions) |
| `requirements.txt` | Python dependencies |
