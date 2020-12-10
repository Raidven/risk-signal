import streamlit as st
import pandas as pd
import numpy as np



def app():
    st.header('Capital Impact')
    text1 = "Capital impact will arise out of `managing cash shortage aggressively` and `valuation losses` arising out of interest rate yield curve, equity price and foreign exchange rate movements."
    text2 = "Due to aggressive liquidity management, losses will arise out of haircuts from assel sale and increased interest payment from distress borrowing."
    text3 = "At balance sheet line item level, `modified duration`, `equity beta` and `FX delta` have been aggregated. These have been used in conjuction with scenarios to calculate the `valuation impact`."
    text4 = "Data sources of these elements can be changed from the **`Settings`** page."
    st.markdown(text1)
    st.markdown(text2)
    st.markdown(text3)
    st.markdown(text4)