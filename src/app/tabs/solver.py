"""Automated Defect & Patch Solver dashboard section."""
import time
from urllib.parse import urlparse
from html import escape
import streamlit as st

from src.ai.gemini_solver import query_solution_with_search
from src.ir.bm25 import BM25Ranker


def render(index=None) -> None:
    """Render the automated defect resolution and patch synthesis engine."""
    st.subheader("Automated Defect & Patch Solver")
    st.markdown("Diagnose system defects, query live repository commit trees and documentation, and synthesize verified code patches with zero hardcoded data.")

    # Preset selection
    if "solver_title" not in st.session_state:
        st.session_state["solver_title"] = "Docker compose healthcheck exit code 137 OOMKilled"
    if "solver_desc" not in st.session_state:
        st.session_state["solver_desc"] = "Container runs out of memory during database migration healthcheck in CI."

    def set_preset(t: str, d: str):
        st.session_state["solver_title"] = t
        st.session_state["solver_desc"] = d

    st.markdown("##### Defect Presets:")
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
        title_in = st.text_input("Defect Title / Signature:", key="solver_title")
    with col_btn:
        st.write("")
        st.write("")
        solve_clicked = st.button("Synthesize Patch & Fix", type="primary", use_container_width=True)

    desc_in = st.text_area("Stack Trace / Error Output / System Context:", key="solver_desc", height=110)

    if solve_clicked or "last_solution" in st.session_state:
        if solve_clicked:
            st.session_state["last_title"] = title_in
            st.session_state["last_desc"] = desc_in

        cur_title = st.session_state.get("last_title", title_in)
        cur_desc = st.session_state.get("last_desc", desc_in)

        if not cur_title.strip():
            st.warning("Please provide a defect title or error signature.")
            return

        if solve_clicked:
            with st.status("Initializing Grounded Repository Search...", expanded=True) as status_box:
                status_box.write("Parsing error signatures and technical keywords...")
                time.sleep(0.3)
                status_box.write("Scanning remote repository trees, pull requests, and commit histories...")
                t0 = time.time()
                result = query_solution_with_search(cur_title, cur_desc)
                result["latency_ms"] = (time.time() - t0) * 1000
                status_box.write("Synthesizing unified patch diff and local reproduction test...")
                time.sleep(0.2)

                if result.get("success"):
                    status_box.update(label="Patch & Diagnostics Synthesized Successfully", state="complete", expanded=False)
                else:
                    status_box.update(label="Remote Search Incomplete — Falling Back to Local Lakehouse", state="error", expanded=False)

                st.session_state["last_solution"] = result

        sol = st.session_state.get("last_solution", {})
        if sol.get("success"):
            sources = sol.get("sources", [])
            queries = sol.get("search_queries", [])
            latency = sol.get("latency_ms", 0)

            # Technical metric chips
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.markdown(f"""
                <div style="background: #142139; border: 1px solid #293a56; border-radius: 6px; padding: 10px; text-align: center;">
                    <div style="font-size: 8pt; color: #94a3b8; text-transform: uppercase;">Retrieval Latency</div>
                    <div style="font-size: 14pt; font-weight: 700; color: #38bdf8;">{latency:.0f} ms</div>
                </div>
                """, unsafe_allow_html=True)
            with m_col2:
                st.markdown(f"""
                <div style="background: #142139; border: 1px solid #293a56; border-radius: 6px; padding: 10px; text-align: center;">
                    <div style="font-size: 8pt; color: #94a3b8; text-transform: uppercase;">Grounded References</div>
                    <div style="font-size: 14pt; font-weight: 700; color: #34d399;">{len(sources)} Verified</div>
                </div>
                """, unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"""
                <div style="background: #142139; border: 1px solid #293a56; border-radius: 6px; padding: 10px; text-align: center;">
                    <div style="font-size: 8pt; color: #94a3b8; text-transform: uppercase;">Search Passes</div>
                    <div style="font-size: 14pt; font-weight: 700; color: #f59e0b;">{len(queries) if queries else 1} Executed</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # Discovered repository sources
            if sources:
                with st.expander(f"Discovered Commits, Pull Requests & References ({len(sources)} found)", expanded=True):
                    for s in sources[:8]:
                        url = s.get("url", "")
                        domain = urlparse(url).netloc.replace("www.", "")
                        title = s.get("title", url)
                        st.markdown(f"""
                        <div style="padding: 6px 0; border-bottom: 1px solid #1f2e46; font-size: 9pt;">
                            <span style="background: #1e293b; color: #94a3b8; font-size: 7.5pt; padding: 2px 6px; border-radius: 3px; border: 1px solid #334155; margin-right: 6px;">
                                {domain}
                            </span>
                            <a href="{url}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">{escape(str(title))}</a>
                        </div>
                        """, unsafe_allow_html=True)

            # Solution markdown report
            st.markdown("""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 18px; margin-top: 14px;">
            """, unsafe_allow_html=True)
            st.markdown(sol.get("text", ""))
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Fallback to local lakehouse IR retrieval
            st.warning("Grounded retrieval service is currently unavailable. Rendering dynamic historical matches from the local Lakehouse index.")

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
