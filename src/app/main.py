"""Streamlit Interactive Analytics, Search, and Classification Dashboard.

Provides an executive and engineering UI across 4 tabs:
1. Trends & Metrics: OLAP analytics over DuckDB star schema.
2. Search: BM25 and Unigram LM query engine over GitHub issues.
3. Classifier: Real-time ML prediction for bug/enhancement/doc/question.
4. Data Quality: Mathematical row reconciliation and drop audit trail.
"""

import json
from pathlib import Path
import duckdb
import pyarrow.parquet as pq

try:
    import streamlit as st
except ImportError:
    st = None

from src.common.config import PROJECT_ROOT, CURATED_DATA_DIR, CLEAN_DATA_DIR
from src.ir.index import InvertedIndex, tokenize
from src.ir.bm25 import BM25Ranker
from src.ir.lm import LanguageModelRanker
from src.ir.naive_bayes import MultinomialNaiveBayes


def load_dq_report() -> dict:
    """Load data quality audit report."""
    report_file = CLEAN_DATA_DIR / "dq_report.json"
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_app() -> None:
    """Render Streamlit user interface."""
    if st is None:
        print("Streamlit not installed. Install via pip install streamlit.")
        return

    st.set_page_config(page_title="GH Archive Lakehouse & ML Engine", layout="wide")
    st.title("GH Archive Lakehouse & ML Intelligence Hub")
    st.markdown("Student: **Hassan** | Architecture: **Parquet -> DuckDB -> PySpark -> IR/ML**")

    tab1, tab2, tab3, tab4 = st.tabs(["Trends & OLAP", "Issue Search (BM25/LM)", "Issue Classifier (NB)", "Data Quality Audit"])

    db_path = PROJECT_ROOT / "data" / "lakehouse.duckdb"

    # Tab 1: OLAP Analytics
    with tab1:
        st.header("Lakehouse OLAP Metrics")
        if db_path.exists():
            con = duckdb.connect(str(db_path), read_only=True)
            col1, col2, col3 = st.columns(3)
            total_events = con.execute("SELECT count(*) FROM fact_events").fetchone()[0]
            total_repos = con.execute("SELECT count(*) FROM dim_repo").fetchone()[0]
            total_actors = con.execute("SELECT count(*) FROM dim_actor").fetchone()[0]
            col1.metric("Total Clean Events", f"{total_events:,}")
            col2.metric("Unique Repositories", f"{total_repos:,}")
            col3.metric("Active Pseudonymised Actors", f"{total_actors:,}")

            st.subheader("Top Repositories by Activity")
            top_repos = con.execute("""
                SELECT r.repo_name, count(*) as event_count
                FROM fact_events f
                JOIN dim_repo r ON f.repo_key = r.repo_key
                GROUP BY r.repo_name
                ORDER BY event_count DESC
                LIMIT 10
            """).fetchdf()
            st.dataframe(top_repos, use_container_width=True)

            st.subheader("Hourly Event Volume")
            hourly = con.execute("""
                SELECT hour, count(*) as total_events
                FROM fact_events
                GROUP BY hour
                ORDER BY hour
            """).fetchdf()
            st.bar_chart(hourly.set_index("hour"))
            con.close()
        else:
            st.warning("Lakehouse DuckDB database not found.")

    # Tab 2: IR Search
    with tab2:
        st.header("Information Retrieval Engine")
        splits_path = CURATED_DATA_DIR / "splits.parquet"
        if splits_path.exists():
            table = pq.read_table(splits_path)
            docs = table.to_pylist()
            index = InvertedIndex()
            for d in docs[:5000]:  # Cache top 5,000 for responsive search demo
                index.add_document(d["event_id"], f"{d['title']} {d['body']}", metadata=d)
            index.finalize()

            query = st.text_input("Enter search keywords:", "memory leak")
            model_choice = st.radio("Retrieval Model:", ["BM25", "Language Model (Dirichlet)"])

            if query:
                if model_choice == "BM25":
                    ranker = BM25Ranker(index)
                    results = ranker.score_query(query, top_k=5)
                else:
                    lm = LanguageModelRanker(index)
                    results = lm.score_query(query, top_k=5)

                st.subheader(f"Top Matches ({len(results)} found)")
                for doc_id, score in results:
                    meta = index.doc_metadata.get(doc_id, {})
                    with st.expander(f"[{meta.get('label', 'issue').upper()}] {meta.get('title', 'Untitled')} (Score: {score:.3f})"):
                        st.write(f"**Repository**: {meta.get('repo_name', 'unknown')}")
                        st.write(f"**Issue #**: {meta.get('issue_number', 'N/A')}")
                        st.write(meta.get("body", "No description provided.")[:300] + "...")
        else:
            st.warning("Curated splits not found. Run src/ir/split.py first.")

    # Tab 3: Classifier
    with tab3:
        st.header("Software Issue Category Classifier")
        st.write("Predicts whether an issue is a **bug**, **enhancement**, **documentation**, or **question**.")
        user_title = st.text_input("Issue Title:", "Segmentation fault on startup when loading config")
        user_body = st.text_area("Issue Body:", "The server crashes immediately after launching with SIGSEGV.")

        if st.button("Classify Issue"):
            splits_path = CURATED_DATA_DIR / "splits.parquet"
            if splits_path.exists():
                table = pq.read_table(splits_path)
                train_docs = [d for d in table.to_pylist() if d["split"] == "train"]
                nb = MultinomialNaiveBayes()
                nb.fit([f"{d['title']} {d['body']}" for d in train_docs], [d["label"] for d in train_docs])
                pred = nb.predict(f"{user_title} {user_body}")
                probs = nb.predict_log_proba(f"{user_title} {user_body}")

                st.success(f"Predicted Class: **{pred.upper()}**")
                st.json(probs)

    # Tab 4: DQ Audit
    with tab4:
        st.header("Data Quality & Row Reconciliation Audit")
        report = load_dq_report()
        if report:
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows Read (Raw)", f"{report.get('rows_read', 0):,}")
            c2.metric("Rows Kept (Silver)", f"{report.get('rows_kept', 0):,}")
            c3.metric("Rows Dropped", f"{report.get('total_dropped', 0):,}")

            st.write(f"**Reconciliation Status**: {'Passed (Zero Silent Drops)' if report.get('reconciled') else 'FAILED'}")
            st.subheader("Drop Reasons Breakdown")
            st.json(report.get("drop_breakdown", {}))
        else:
            st.warning("DQ report not found.")


if __name__ == "__main__":
    render_app()
