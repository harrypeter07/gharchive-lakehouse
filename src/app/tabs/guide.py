"""Technical system documentation and developer profile."""
import streamlit as st
from src.common.config import PROJECT_ROOT


def render() -> None:
    """Display the technical architecture and engineering specification."""
    st.subheader('About the Developer & System Architecture')
    path = PROJECT_ROOT/'docs'/'DL_LAB_GUIDE.md'
    if path.exists():
        st.markdown(path.read_text(encoding='utf-8'))
    else:
        st.info('The documentation file is not available.')
