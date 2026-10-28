"""AI Issue Solver and Solution Synthesizer dashboard section."""
import os
import time
from html import escape
import streamlit as st

from src.ai.gemini_solver import query_gemini_with_search
from src.ir.bm25 import BM25Ranker
from src.app.tabs.search import extract_highlighted_snippet, TRIAGE_GUIDANCE


def render(index=None) -> None:
    """Render the AI-assisted issue solution and live web search engine."""
    st.subheader("AI Issue Solver & Solution Synthesizer")
    st.markdown("Diagnose technical issues, search live across GitHub and the web for known repository fixes, and synthesize actionable code patches.")

    # API Key management
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if "gemini_api_key" not in st.session_state:
        st.session_state["gemini_api_key"] = env_key

    with st.expander("Gemini API Configuration (Web Grounding)", expanded=not bool(st.session_state["gemini_api_key"])):
        col_k, col_info = st.columns([2, 1])
        with col_k:
            key_input = st.text_input(
                "Gemini API Key:",
                value=st.session_state.get("gemini_api_key", ""),
                type="password",
                help="Get a free API key at https://aistudio.google.com/app/apikey. Required for live web search grounding.",
                placeholder="AIzaSy..."
            )
            if key_input:
                st.session_state["gemini_api_key"] = key_input.strip()
        with col_info:
            st.markdown("""
            <div style='font-size: 8.5pt; color: #94a3b8; padding-top: 25px;'>
            Free tier works without credit card.<br>
            Supports live Google Search grounding over GitHub repos & commits.
            </div>
            """, unsafe_allow_html=True)

    # Preset selection
    if "solver_title" not in st.session_state:
        st.session_state["solver_title"] = "Docker compose healthcheck exit code 137 OOMKilled"
    if "solver_desc" not in st.session_state:
        st.session_state["solver_desc"] = "Container runs out of memory during database migration healthcheck in CI."

    def set_preset(t: str, d: str):
        st.session_state["solver_title"] = t
        st.session_state["solver_desc"] = d

    st.markdown("##### Quick Issue Presets:")
    p_cols = st.columns(4)
    p_cols[0].button("Docker healthcheck 137", on_click=set_preset,
                     args=("Docker compose healthcheck exit code 137 OOMKilled",
                           "Container runs out of memory during database migration healthcheck in CI."))
    p_cols[1].button("Go connection pool leak", on_click=set_preset,
                     args=("Go http client connection reset by peer memory leak",
                           "HTTP transport idle connections not closing properly leading to socket exhaustion."))
    p_cols[2].button("Postgres concurrent deadlock", on_click=set_preset,
                     args=("Postgres deadlock detected during concurrent batch upsert",
                           "Multiple worker threads updating the same table in non-deterministic row order."))
    p_cols[3].button("Python asyncio event loop", on_click=set_preset,
                     args=("RuntimeError: Event loop is closed in cleanup",
                           "Asyncio loop closed before background task finished execution during graceful shutdown."))

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        title_in = st.text_input("Issue Title / Summary:", key="solver_title")
    with col_btn:
        st.write("")
        st.write("")
        solve_clicked = st.button("Generate Solution", type="primary", use_container_width=True)

    desc_in = st.text_area("Detailed Stack Trace / Logs / Context:", key="solver_desc", height=100)

    # Execution
    active_key = st.session_state.get("gemini_api_key", "").strip()

    if solve_clicked or "last_solution" in st.session_state:
        if solve_clicked:
            st.session_state["last_title"] = title_in
            st.session_state["last_desc"] = desc_in

        cur_title = st.session_state.get("last_title", title_in)
        cur_desc = st.session_state.get("last_desc", desc_in)

        if not cur_title.strip():
            st.warning("Please provide an issue title or error message.")
            return

        if active_key:
            if solve_clicked:
                with st.spinner("Searching GitHub repositories and synthesizing code fix via Google Search Grounding..."):
                    t0 = time.time()
                    result = query_gemini_with_search(active_key, cur_title, cur_desc)
                    result["latency_ms"] = (time.time() - t0) * 1000
                    st.session_state["last_solution"] = result

            sol = st.session_state.get("last_solution", {})
            if sol.get("success"):
                st.success(f"Grounded Solution Generated in {sol.get('latency_ms', 0):.0f} ms via {sol.get('model', 'gemini-2.0-flash')} with Google Search")

                # Web search grounding queries & sources
                sources = sol.get("sources", [])
                queries = sol.get("search_queries", [])
                if sources or queries:
                    with st.expander("Discovered Web & GitHub Sources", expanded=True):
                        if queries:
                            st.markdown(f"**Google Search Queries:** `{', '.join(queries)}`")
                        if sources:
                            st.markdown("**Discovered Reference Links:**")
                            for s in sources[:8]:
                                st.markdown(f"- [{s['title']}]({s['url']})")

                # Main solution markdown
                st.markdown("### Technical Solution & Code Fix")
                st.markdown(sol.get("text", ""))

            else:
                st.error(f"AI Solution Failed: {sol.get('error', 'Unknown error')}")

        else:
            # Fallback to local lakehouse IR retrieval
            st.info("No Gemini API key provided. Showing similar historical resolutions from the local Lakehouse index. To enable live web search and automated code patch synthesis across GitHub, enter a free Gemini API key above.")

            if index:
                ranker = BM25Ranker(index)
                results = ranker.score_query_detailed(f"{cur_title} {cur_desc}", top_k=3)

                st.markdown("### Top Lakehouse Historical Matches")
                for rank, item in enumerate(results, 1):
                    meta = index.doc_metadata.get(item["doc_id"], {})
                    t = meta.get("title", "Untitled")
                    lbl = meta.get("label", "issue")
                    repo = meta.get("repo_name", "unknown")
                    b = meta.get("body", "")
                    st.markdown(f"""
                    <div style='background-color: #142139; border: 1px solid #293a56; border-radius: 8px; padding: 12px; margin-bottom: 10px;'>
                        <b>#{rank}. {escape(str(t))}</b> &bull; <code>{escape(str(repo))}</code> &bull; <span class='badge badge-{lbl}'>{lbl}</span>
                        <div style='font-size: 8.5pt; color: #94a3b8; margin-top: 6px;'>
                            {escape(str(b)[:240])}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
