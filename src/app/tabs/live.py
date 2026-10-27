"""Download-only control: never claim transformation that was not executed."""
import streamlit as st
from src.common.config import RAW_DATA_DIR
from src.ingest.download_gharchive import fetch_hour_file


def render() -> None:
    """Fetch one archive and report only the download outcome."""
    st.subheader('Hourly archive download')
    st.write('Download a raw GH Archive file. Cleaning and warehouse refresh are separate pipeline commands.')
    hour = st.selectbox('Archive hour (UTC)', ['2024-06-10-15', '2026-10-24-15'])
    if st.button('Download archive', type='primary'):
        date, number = hour.rsplit('-', 1)
        try:
            with st.spinner('Downloading archive…'):
                result = fetch_hour_file(date, int(number), RAW_DATA_DIR)
            st.success('Download finished. No cleaning or warehouse refresh was performed here.')
            st.json(result)
        except Exception as error:
            st.warning(f'Download failed: {error}')
