import streamlit as st
import pandas as pd
import numpy as np



def app():
    st.header('Share report with others (coming soon...)')
    st.radio('file type',('pdf', 'docx', 'pptx', 'html'))
    st.button('Download')
