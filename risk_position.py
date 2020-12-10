import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def app():
    st.header('Risk Position')
    st.markdown('Risk positions of overall bank is combination of portfolio positions, inherent risk profiles and probable external events.')
    st.markdown('Data sources of these elements can be changed from the **`Settings`** page.')
    