"""Plain language practical alignment for an honest lab presentation."""
import streamlit as st
from src.common.config import PROJECT_ROOT


def render() -> None:
    """Display the same lab explanation delivered in the project documentation."""
    st.subheader('Lab presentation guide')
    path = PROJECT_ROOT/'docs'/'DL_LAB_GUIDE.md'
    if path.exists():
        st.markdown(path.read_text(encoding='utf-8'))
    else:
        st.info('The lab guide has not been generated yet.')
