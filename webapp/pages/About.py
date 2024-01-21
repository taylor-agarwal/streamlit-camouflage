import os
import pathlib

import streamlit as st

from webapp.utils.constants import TITLE_HTML 


DIRECTORY_PATH = pathlib.Path(os.path.abspath(__file__)).parent.parent

st.markdown(TITLE_HTML, unsafe_allow_html=True)

with open(DIRECTORY_PATH / "markdown" / "About.md") as f:
    st.markdown(f.read())

clicked = st.button(label="Return to Camouflage", use_container_width=True)
if clicked:
    st.switch_page("Camouflage.py")