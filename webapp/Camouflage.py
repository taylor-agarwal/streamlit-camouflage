import sys

import streamlit as st

sys.path.insert(0, ".")

from webapp.utils.constants import HIDE_FOOTER_STYLE, TITLE_HTML, COLUMN_STYLE

# Hide streamlit header and footer
st.markdown(HIDE_FOOTER_STYLE, unsafe_allow_html=True)

st.write(COLUMN_STYLE, unsafe_allow_html=True)

st.markdown("#")

st.write(TITLE_HTML, unsafe_allow_html=True)

st.markdown("##")

outfit_analyzer_clicked = st.button(label="Outfit Analyzer", use_container_width=True)
if outfit_analyzer_clicked:
    st.switch_page("pages/Outfit Analyzer.py")

help_clicked = st.button(label="How do I use this app?", use_container_width=True)
if help_clicked:
    st.switch_page("pages/About.py")
