import streamlit as st
import pandas as pd

from reports import to_json_str, to_csv_str, to_markdown, parse_citations, clean_filename
from scraper import scrape_scholar

st.set_page_config(page_title="Literature Research Dashboard", page_icon="📚", layout="centered")

# Mobile-friendly tweaks: full-width buttons, comfortable padding on small screens
st.markdown("""
<style>
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    h1 { font-size: 1.6rem !important; }
    .stButton > button { width: 100%; padding: 0.75rem 1rem; font-size: 1rem; }
    .stDownloadButton > button { width: 100%; padding: 0.75rem 1rem; }
    .stTextInput > div > div > input { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

SAMPLE_PAPERS = [
    {"Rank": 1, "Title": "Attention Is All You Need",
     "Authors_and_Year": "Vaswani et al. - 2017", "Citations": "120,456",
     "Link": "https://arxiv.org/abs/1706.03762",
     "Abstract_Snippet": "We propose the Transformer, a model architecture eschewing recurrence and relying entirely on attention mechanisms."},
    {"Rank": 2, "Title": "BERT: Pre-training of Deep Bidirectional Transformers",
     "Authors_and_Year": "Devlin et al. - 2019", "Citations": "98,312",
     "Link": "https://arxiv.org/abs/1810.04805",
     "Abstract_Snippet": "We introduce a new language representation model designed to pre-train deep bidirectional representations."},
    {"Rank": 3, "Title": "Language Models are Few-Shot Learners",
     "Authors_and_Year": "Brown et al. - 2020", "Citations": "45,209",
     "Link": "https://arxiv.org/abs/2005.14165",
     "Abstract_Snippet": "We show that scaling up language models greatly improves task-agnostic, few-shot performance."},
    {"Rank": 4, "Title": "Deep Residual Learning for Image Recognition",
     "Authors_and_Year": "He et al. - 2016", "Citations": "156,780",
     "Link": "https://arxiv.org/abs/1512.03385",
     "Abstract_Snippet": "We present a residual learning framework to ease the training of substantially deeper networks."},
    {"Rank": 5, "Title": "Generative Adversarial Networks",
     "Authors_and_Year": "Goodfellow et al. - 2014", "Citations": "89,431",
     "Link": "https://arxiv.org/abs/1406.2661",
     "Abstract_Snippet": "We propose a new framework for estimating generative models via an adversarial process."},
]

st.title("📚 Literature Research Dashboard")
st.caption("Search Google Scholar, review the top papers, and export professional reports.")

if "papers" not in st.session_state:
    st.session_state.papers = []
if "query" not in st.session_state:
    st.session_state.query = ""

with st.form("search_form"):
    q = st.text_input("Research topic", placeholder="e.g. transformer models for medical imaging")
    c1, c2 = st.columns(2)
    go = c1.form_submit_button("🔍 Search Scholar")
    demo = c2.form_submit_button("✨ Load demo data")

if go:
    if not q.strip():
        st.warning("Please enter a research topic first.")
    else:
        with st.spinner("Scraping Google Scholar — first search installs the browser (~1–2 min), later ones ~20 sec..."):
            papers, status = scrape_scholar(q.strip())
        st.session_state.query = q.strip()
        st.session_state.papers = papers
        if status == "blocked":
            st.warning("⚠️ Google Scholar blocked the automated request (CAPTCHA / bot check). "
                       "Try the demo data below, or run the search manually in your browser.")
        elif status == "empty":
            st.info("No results found for this topic. Try different keywords.")
        else:
            st.success("Found {} papers.".format(len(papers)))

if demo:
    st.session_state.papers = SAMPLE_PAPERS
    st.session_state.query = "Demo topic"

papers = st.session_state.papers
if papers:
    df = pd.DataFrame(papers)
    df["Citations_n"] = df["Citations"].apply(parse_citations)

    m1, m2, m3 = st.columns(3)
    m1.metric("Papers", len(df))
    m2.metric("Total citations", "{:,}".format(int(df["Citations_n"].sum())))
    m3.metric("Avg citations", "{:,.1f}".format(df["Citations_n"].mean()))

    st.subheader("📊 Citations per paper")
    chart_df = df[["Title", "Citations_n"]].copy()
    chart_df["Title"] = chart_df["Title"].str.slice(0, 38)
    st.bar_chart(chart_df.set_index("Title"))

    st.subheader("📄 Results")
    st.dataframe(df[["Rank", "Title", "Authors_and_Year", "Citations"]],
                 use_container_width=True, hide_index=True)

    for p in papers:
        with st.expander("{}. {}".format(p["Rank"], p["Title"][:70])):
            st.write("**Authors/Year:** {} | **Citations:** {}".format(
                p["Authors_and_Year"], p["Citations"]))
            st.write(p["Abstract_Snippet"])
            if p["Link"]:
                st.markdown("[🔗 Open source]({})".format(p["Link"]))

    st.subheader("⬇️ Export reports")
    base = clean_filename(st.session_state.query)
    d1, d2, d3 = st.columns(3)
    d1.download_button("JSON", to_json_str(papers),
                       file_name="{}.json".format(base), mime="application/json")
    d2.download_button("CSV", to_csv_str(papers).encode("utf-8"),
                       file_name="{}_matrix.csv".format(base), mime="text/csv")
    d3.download_button("Markdown", to_markdown(papers, st.session_state.query),
                       file_name="{}_report.md".format(base), mime="text/markdown")
else:
    st.info("👆 Enter a topic and press **Search Scholar**, or load **demo data** to explore the dashboard.")
