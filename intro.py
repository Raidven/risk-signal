import streamlit as st
import pandas as pd
import numpy as np

def app():
    st.header('Understanding of the balance sheet')
    st.write('Liquidity signal tracks current risk position of the bank. It also estimates probable cash positions in subsequent 30 days if the risk level continues. Under those circumstamces, capital impact is also projected')
    st.markdown('Data sources of these elements can be changed from the **`Settings`** page.')
    