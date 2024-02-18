import os
import pathlib
import sys

import streamlit as st

sys.path.insert(0, ".")

from webapp.utils.constants import PAGE_HEADER_HTML, HIDE_FOOTER_STYLE, COLUMN_STYLE


DIRECTORY_PATH = pathlib.Path(os.path.abspath(__file__)).parent.parent

# Hide streamlit header and footer
st.markdown(HIDE_FOOTER_STYLE, unsafe_allow_html=True)

st.write(COLUMN_STYLE, unsafe_allow_html=True)

st.markdown("#")

st.write(PAGE_HEADER_HTML, unsafe_allow_html=True)

with open(DIRECTORY_PATH / "markdown" / "About.md") as f:
    st.markdown(f.read())

clicked = st.button(label="Return to Camouflage", use_container_width=True)
if clicked:
    st.switch_page("Camouflage.py")