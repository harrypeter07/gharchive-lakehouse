from pathlib import Path
import re
import time
from html import escape
import streamlit as st
from src.ir.bm25 import BM25Ranker
from src.ir.lm import LanguageModelRanker
from src.ir.index import tokenize


TRIAGE_GUIDANCE = {
    "bug": "Defect Triage: Verify crash reproduction steps, inspect stack trace line numbers, and isolate memory/thread state.",
    "enhancement": "Feature Proposal: Review API ergonomics, benchmark throughput overhead, and check backward compatibility.",
    "documentation": "Documentation: Verify accurate code examples, validate CLI syntax, and update configuration guides.",
    "question": "Configuration Support: Reference official setup manuals, provide minimal working snippet, and review environment variables."
}


def extract_highlighted_snippet(text: str, matched_terms: list[str], max_chars: int = 300) -> str:
    """Locate the first occurrence of query terms and extract a formatted window with highlighted keywords."""
    if not text:
        return "<i style='color: #64748b;'>No issue description provided.</i>"

    lower_text = text.lower()
    first_pos = -1
    for term in matched_terms:
        pos = lower_text.find(term.lower())
        if pos != -1 and (first_pos == -1 or pos < first_pos):
            first_pos = pos

    if first_pos == -1:
        snippet = text[:max_chars]
        suffix = "..." if len(text) > max_chars else ""
        escaped_snippet = escape(snippet + suffix)
    else:
        start = max(0, first_pos - 60)
        end = min(len(text), start + max_chars)
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        escaped_snippet = escape(prefix + text[start:end] + suffix)

    for term in matched_terms:
        pattern = re.compile(re.escape(escape(term)), re.IGNORECASE)
        escaped_snippet = pattern.sub(
            lambda m: f"<span style='color: #38bdf8; font-weight: 700; background: rgba(56, 189, 248, 0.2); padding: 1px 4px; border-radius: 3px;'>{m.group(0)}</span>",
            escaped_snippet
        )

    return escaped_snippet


def render(index, nb_model, all_records) -> None:
    """Render the high-precision probabilistic defect and issue search engine."""

    if "search_query" not in st.session_state:
        st.session_state['search_query'] = 'memory leak connection pool'
    st.subheader("Intelligent Defect & Issue Search Engine")
    st.markdown("Discover relevant bugs, pull requests, and configuration discussions across **14,780 indexed issues** using probabilistic keyword ranking with query coordination matching.")

    def set_search(q):
        st.session_state["search_query"] = q

    st.markdown("##### Quick Query Presets:")
    q_cols = st.columns(4)
    q_cols[0].button("memory leak connection pool", on_click=set_search, args=("memory leak connection pool",))
    q_cols[1].button("segmentation fault core dumped", on_click=set_search, args=("segmentation fault core dumped",))
    q_cols[2].button("docker compose healthcheck", on_click=set_search, args=("docker compose healthcheck",))
    q_cols[3].button("null pointer exception parser", on_click=set_search, args=("null pointer exception parser",))

    col_q, col_m = st.columns([3, 1])
    with col_q:
        current_query = st.text_input("Search keywords:", key="search_query")
    with col_m:
        ir_model = st.radio("Ranking Algorithm:", ["Okapi BM25 Ranking", "Probabilistic Language Model (Dirichlet)"])

    filter_cols = st.columns([2, 2, 2])
    with filter_cols[0]:
        cat_filter = st.selectbox("Category Filter:", ["All Categories", "bug", "enhancement", "documentation", "question"])
    with filter_cols[1]:
        min_match_opt = st.selectbox("Precision Threshold:", ["All Matches (any term)", "At least 50% term match", "High Precision (100% terms)"])
    with filter_cols[2]:
        top_k_val = st.selectbox("Results Count:", [6, 10, 15], index=0)

    min_ratio = 0.0
    if "50%" in min_match_opt:
        min_ratio = 0.50
    elif "100%" in min_match_opt:
        min_ratio = 1.00

    if index and current_query:
        start_t = time.time()
        if "BM25" in ir_model:
            ranker = BM25Ranker(index, k1=1.5, b=0.75)
            detailed_results = ranker.score_query_detailed(current_query, top_k=top_k_val * 3, min_match_ratio=min_ratio)
        else:
            lm = LanguageModelRanker(index, mu=2000.0)
            detailed_results = lm.score_query_detailed(current_query, top_k=top_k_val * 3, min_match_ratio=min_ratio)

        # Apply category filter
        if cat_filter != "All Categories":
            filtered = [r for r in detailed_results if index.doc_metadata.get(r["doc_id"], {}).get("label") == cat_filter]
        else:
            filtered = detailed_results

        final_results = filtered[:top_k_val]
        elapsed = (time.time() - start_t) * 1000

        st.caption(f"Retrieved {len(final_results)} relevant issues in {elapsed:.2f} ms across {index.doc_count:,} indexed records.")

        if not final_results:
            st.info("No documents matched the specified filters. Try lowering the precision threshold or broadening your keywords.")

        for rank, item in enumerate(final_results, 1):
            doc_id = item["doc_id"]
            score = item["score"]
            matched_terms = item["matched_terms"]
            matched_count = item["matched_count"]
            total_query_terms = item["total_query_terms"]
            match_ratio = item["match_ratio"]

            meta = index.doc_metadata.get(doc_id, {})
            lbl = meta.get("label", "issue")
            badge_class = f"badge-{lbl}"
            repo_name = meta.get("repo_name", "unknown")
            issue_num = meta.get("issue_number", "N/A")
            title = meta.get("title", "Untitled")
            body = meta.get("body", "")

            # Match badge styling
            pct = match_ratio * 100
            if pct >= 100:
                match_color = "#34d399"
                match_bg = "rgba(52, 211, 153, 0.15)"
            elif pct >= 66:
                match_color = "#38bdf8"
                match_bg = "rgba(56, 189, 248, 0.15)"
            elif pct >= 50:
                match_color = "#fbbf24"
                match_bg = "rgba(251, 191, 36, 0.15)"
            else:
                match_color = "#94a3b8"
                match_bg = "rgba(148, 163, 184, 0.15)"

            snippet_html = extract_highlighted_snippet(body, matched_terms, max_chars=320)
            guidance = TRIAGE_GUIDANCE.get(lbl, "Review issue description and verify system behavior.")

            github_url = f"https://github.com/{repo_name}/issues/{issue_num}" if repo_name != "unknown" and issue_num != "N/A" else None
            github_link_html = f"<a href='{github_url}' target='_blank' style='color: #60a5fa; text-decoration: none;'>View on GitHub ↗</a>" if github_url else ""

            st.markdown(f"""
            <div style="background-color: #142139; border: 1px solid #293a56; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                    <div>
                        <span style="font-weight: 700; font-size: 11pt; color: #e8f0ff;">#{rank}. {escape(str(title))}</span>
                    </div>
                    <div style="display: flex; gap: 6px; align-items: center; flex-shrink: 0;">
                        <span style="background: {match_bg}; color: {match_color}; font-weight: 700; font-size: 8.5pt; padding: 2px 8px; border-radius: 4px; border: 1px solid {match_color}40;">
                            {pct:.0f}% Term Match ({matched_count}/{total_query_terms})
                        </span>
                        <span class="badge {badge_class}">{lbl}</span>
                    </div>
                </div>
                <div style="font-size: 8.5pt; color: #95a9c6; margin: 6px 0;">
                    <b>Repo:</b> <code>{escape(str(repo_name))}</code> &bull; 
                    <b>Issue #:</b> #{issue_num} &bull; 
                    <b>Score:</b> <code>{score:.3f}</code> &bull; 
                    <b>Matched Words:</b> <code style="color: #38bdf8;">{', '.join(matched_terms) if matched_terms else 'none'}</code> 
                    {f'&bull; {github_link_html}' if github_link_html else ''}
                </div>
                <div style="font-size: 9pt; color: #cbd5e1; background: #0c1626; padding: 10px; border-radius: 6px; border: 1px solid #1f2e46; line-height: 1.5; margin: 8px 0;">
                    {snippet_html}
                </div>
                <div style="font-size: 8.5pt; color: #93c5fd; background: rgba(59, 130, 246, 0.1); padding: 6px 10px; border-radius: 4px; border-left: 3px solid #3b82f6;">
                    <b>Maintainer Action:</b> {guidance}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if index is None:
        st.warning("Search data is missing. Restore the curated splits to enable search.")
