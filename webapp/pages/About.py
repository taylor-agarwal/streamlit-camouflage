import os
import pathlib

import streamlit as st


DIRECTORY_PATH = pathlib.Path(os.path.abspath(__file__)).parent.parent

with open(DIRECTORY_PATH / "markdown" / "About.md") as f:
    st.markdown(f.read())

