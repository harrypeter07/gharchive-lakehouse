from pathlib import Path
import time
from html import escape
import duckdb
import streamlit as st
from src.ir.bm25 import BM25Ranker
from src.ir.lm import LanguageModelRanker


def render(index, nb_model, all_records) -> None:
    """Render this focused dashboard section."""

    if "search_query" not in st.session_state:
        st.session_state['search_query'] = 'memory leak connection pool'
    st.subheader("Intelligent Defect & Issue Search Engine")
    st.markdown("Instantly discover duplicate bugs and related technical tickets across the indexed training issues using probabilistic keyword ranking.")

    def set_search(q):
        st.session_state["search_query"] = q

    st.markdown("##### Quick Query Presets:")
    q_cols = st.columns(4)
    q_cols[0].button("💡 memory leak connection pool", on_click=set_search, args=("memory leak connection pool",))
    q_cols[1].button("💡 segmentation fault core dumped", on_click=set_search, args=("segmentation fault core dumped",))
    q_cols[2].button("💡 docker compose healthcheck", on_click=set_search, args=("docker compose healthcheck",))
    q_cols[3].button("💡 null pointer exception parser", on_click=set_search, args=("null pointer exception parser",))

    col_q, col_m = st.columns([3, 1])
    with col_q:
        current_query = st.text_input("Search keywords:", key="search_query")
    with col_m:
        ir_model = st.radio("Ranking Algorithm:", ["Okapi BM25 Ranking", "Probabilistic Language Model (Dirichlet)"])

    if index and current_query:
        start_t = time.time()
        if "BM25" in ir_model:
            ranker = BM25Ranker(index, k1=1.5, b=0.75)
            results = ranker.score_query(current_query, top_k=6)
        else:
            lm = LanguageModelRanker(index, mu=2000.0)
            results = lm.score_query(current_query, top_k=6)
        elapsed = (time.time() - start_t) * 1000

        st.caption(f"⚡ Retrieved {len(results)} relevant documents in {elapsed:.2f} ms across {index.doc_count:,} indexed issues.")

        for rank, (doc_id, score) in enumerate(results, 1):
            meta = index.doc_metadata.get(doc_id, {})
            lbl = meta.get("label", "issue")
            badge_class = f"badge-{lbl}"
            with st.container():
                st.markdown(f"""
                <div style="background-color: #142139; border: 1px solid #293a56; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 11pt; color: #e8f0ff;">#{rank}. {escape(str(meta.get('title', 'Untitled')))}</span>
                        <span class="badge {badge_class}">{lbl}</span>
                    </div>
                    <div style="font-size: 8.5pt; color: #95a9c6; margin: 4px 0;">
                        <b>Repo:</b> {escape(str(meta.get('repo_name', 'unknown')))} &bull; <b>Issue #:</b> {meta.get('issue_number', 'N/A')} &bull; <b>Relevance Score:</b> <code>{score:.3f}</code>
                    </div>
                    <div style="font-size: 9pt; color: #b8c8df;">
                        {escape(str(meta.get('body', ''))[:280])}...
                    </div>
                </div>
                """, unsafe_allow_html=True)

    if index is None:
        st.warning("Search data is missing. Restore the curated splits to enable search.")
    elif current_query and not results:
        st.info("No matching issues. Try fewer or different keywords.")
