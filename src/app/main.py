"""GH Archive dashboard entry point; each section owns its rendering."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from src.app.theme import apply_theme
from src.app.resources import load_ir_and_nb_models
from src.app.tabs import analytics, search, deep_learning, solver, live, guide
from src.common.config import PROJECT_ROOT, CURATED_DATA_DIR

st.set_page_config(page_title="GH Archive | Neural Analytics", page_icon="◈", layout="wide")
apply_theme()
st.markdown('''<div class="masthead"><div><div class="eyebrow">GH ARCHIVE / ANALYTICS LAB</div>
<h1>From GitHub activity to issue intelligence</h1>
<p>Hassan · Lakehouse analytics & information retrieval laboratory</p></div></div>''', unsafe_allow_html=True)
section = st.radio('Workspace', ['Overview', 'Issue search', 'Search categories', 'Issue solver', 'Archive download', 'About me'],
                   horizontal=True, label_visibility='collapsed')
try:
    if section == 'Overview':
        db = PROJECT_ROOT/'data'/'lakehouse.duckdb'
        analytics.render(db if db.exists() else CURATED_DATA_DIR/'demo_lakehouse.duckdb')
    elif section == 'Issue search':
        search.render(*load_ir_and_nb_models())
    elif section == 'Search categories':
        deep_learning.render()
    elif section == 'Issue solver':
        index, nb, records = load_ir_and_nb_models()
        solver.render(index)
    elif section == 'Archive download':
        live.render()
    else:
        guide.render()
except Exception as error:
    st.warning(f'This section could not load its local artifacts: {error}')
st.divider()
st.caption('Data: GH Archive · Development source day 2024-06-10 · Counts reflect the local artifacts. Predictions need human review.')
