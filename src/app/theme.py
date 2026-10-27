"""One consistent navy dashboard theme, including custom result cards."""
import streamlit as st


def apply_theme() -> None:
    """Match the compact blue analytics reference without pale result panels."""
    st.markdown('''<style>
    .stApp {background:#0b1222;color:#e8f0ff}
    [data-testid="stHeader"] {background:#0b1222}
    .block-container {padding-top:1.6rem;max-width:1480px}
    h1 {font-size:1.65rem!important;letter-spacing:-.04em}
    h2,h3 {letter-spacing:-.025em}
    [data-testid="stMetric"], .kpi-card {background:#142139;border:1px solid #293a56;
       border-radius:10px;padding:16px;text-align:left}
    .kpi-val {font-size:1.8rem;font-weight:750;color:#46c6ef}
    .kpi-lbl {font-size:.75rem;color:#a5b6cf;text-transform:uppercase;letter-spacing:.06em}
    [data-testid="stMetricLabel"] {color:#a5b6cf}
    [data-testid="stMetricValue"] {color:#e8f0ff}
    div[data-testid="stVerticalBlockBorderWrapper"]>div {border-color:#293a56!important}
    .stButton>button {border:1px solid #304562;border-radius:7px}
    .stButton>button:hover {border-color:#46c6ef;color:#46c6ef}
    .badge {padding:3px 9px;border-radius:12px;font-size:.7rem;font-weight:700}
    .badge-bug {background:#50243c;color:#ff9fb3}
    .badge-enhancement {background:#123e3e;color:#6fe3c4}
    .badge-documentation {background:#193e60;color:#79d3ff}
    .badge-question {background:#493b28;color:#f9d48a}
    .masthead {display:flex;justify-content:space-between;align-items:center;
      border-bottom:1px solid #293a56;padding:0 0 18px;margin-bottom:16px}
    .eyebrow {color:#46c6ef;font-size:.72rem;letter-spacing:.16em;font-weight:700}
    .masthead p {color:#95a9c6;font-size:.85rem;margin:0}
    </style>''', unsafe_allow_html=True)
