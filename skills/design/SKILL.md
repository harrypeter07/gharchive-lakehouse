# SKILL: design (UI, dashboards, README, architecture)
Use for: Streamlit app, charts, dashboards, README, data-model design. TEXT ONLY: no images or diagrams are produced; describe architecture in short text lists.

## Streamlit
- One file per tab in `src/app/tabs/`, `main.py` only wires them. Sidebar for global controls.
- Top of each tab: one sentence saying what the tab shows. Show row counts and date range so users trust the numbers.
- Heavy work inside `@st.cache_data` / `@st.cache_resource`.
- Handle empty results and errors with `st.warning`, never a crash trace.
- Charts: one message per chart, title says the finding, axes labelled with units, sort bars by value.
- Never display raw usernames; use hashed actor ids or repo-level aggregates.
- Show a small "Data: GH Archive, date X, N events" footer.

## Dashboards (Metabase)
- 3 to 5 cards max. Each answers one business question. Filter by date.

## README structure
1. What and why (3 lines)  2. Data source + citation  3. Architecture as a text list: raw -> clean -> curated -> consumers  4. How to run (copy-paste commands)  5. Results table  6. Limitations (honest)  7. Next steps.

## Data model design
- Name tables `fact_*`, `dim_*`, `agg_*`. State the grain of each fact table: "one row per ...".
