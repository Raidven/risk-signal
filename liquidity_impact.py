import streamlit as st
import pandas as pd
import numpy as np



def app():
    st.header('Liquidity Impact')
    st.markdown('Due to probable risk events, there are likelihoods of higher outflows and lower inflows. Those will impact the cash positions in next 30 days. The base positions and stressed positions are described below.')
    st.markdown('Data sources of these elements can be changed from the **`Settings`** page.')