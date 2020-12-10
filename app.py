import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
cm = sns.color_palette("Blues", as_cmap=True)
import altair as alt




st.title('Liquidity Management')

url_parameter_threshold = './parameters.csv'
url_parameter_value = './parameter_values.csv'
url_balance_sheet = './balance_sheet.csv'
url_cashflow_master_data = './cashflow_master_data.csv'
url_scenarios = './scenarios.csv'

# @st.cache
def load_data(url):
    data = pd.read_csv(url)
    return data

#Create all data frames
threshold = load_data(url_parameter_threshold)
values = load_data(url_parameter_value)
balance_sheet = load_data(url_balance_sheet)
cashflow_config = load_data(url_cashflow_master_data)
scenarios = load_data(url_scenarios)

#Reporting date - user input
date_selected = tuple(values['Date'].unique())        
reporting_date = st.sidebar.selectbox("Select date",date_selected)



#Risk level (RAG) of bank



positions = threshold.join(values.set_index('Parameter_code'), on ='Parameter_code')
positions = positions[(positions['Date']==reporting_date)]
liquidity_flow = cashflow_config.join(balance_sheet.set_index('BS_item_code'), on = 'BS_item_code')
liquidity_flow = liquidity_flow[(liquidity_flow['Date']==reporting_date)]

def RAG_function (Amber_threshold, Red_threshold, Type_threshold, Values):
    if Type_threshold == 'Less':
        if Values <= Red_threshold:
            Score = 9
        elif Values <=Amber_threshold:
            Score = 4
        else:
            Score = 1
    if Type_threshold == 'More':
        if Values >= Red_threshold:
            Score = 9
        elif Values >= Amber_threshold:
            Score = 4
        else:
            Score = 1
    if Type_threshold == 'Equal':
            Score = 4
    return Score

for i in range(len(positions)):
    Amber_threshold = positions.loc[i, 'Amber_threshold']
    Red_threshold = positions.loc[i, 'Red_threshold']
    Type_threshold = positions.loc[i, 'Type_threshold']
    Values = positions.loc[i, 'Values']
    Risk_Score = RAG_function (Amber_threshold, Red_threshold, Type_threshold, Values)
    positions.loc[i, 'Risk_Score'] = Risk_Score
    positions.loc[i, 'Wtd_Risk_Score'] = positions.loc[i, 'Weights'] * Risk_Score
    
Score = positions.groupby('Source_of_crisis').agg(Score_sum = ('Wtd_Risk_Score', sum))
Score['Risk_bucket'] = np.where(Score['Score_sum']<=5, 'green',
                                         np.where(Score['Score_sum']<=7, 'amber', 'red'))
Score = Score.reset_index()
Score['Concat'] = Score['Source_of_crisis'] + "_" + Score['Risk_bucket']

liquidity_flow['stressed_cashflow_factor'] = liquidity_flow['Cashflow_factor_base']
for col_liq in range(liquidity_flow.shape[1]):
    for row_Score in range(Score.shape[0]):
        if liquidity_flow.columns[col_liq]==Score['Concat'].loc[row_Score]:
            liquidity_flow['stressed_cashflow_factor'] = liquidity_flow['stressed_cashflow_factor']*(1+liquidity_flow[liquidity_flow.columns[col_liq]])   
liquidity_flow['Cashflow_amount'] = liquidity_flow['BS_amount']*(liquidity_flow['stressed_cashflow_factor'])
cash_forecast = pd.DataFrame(liquidity_flow.groupby("Source_usage")["Cashflow_amount"].sum()).reset_index()




balance_sheet['Weighted_Duration'] = balance_sheet['BS_amount']*balance_sheet['Duration_IRS']
balance_sheet['Weighted_Beta'] = balance_sheet['BS_amount']*balance_sheet['Beta_equity']
balance_sheet['Weighted_Delta'] = balance_sheet['BS_amount']*balance_sheet['Sensitivity_forex']

BS_Duration_IRS, BS_Beta_S, BS_Delta_FX = list(balance_sheet[balance_sheet['Date']==reporting_date][['Weighted_Duration', 'Weighted_Beta', 'Weighted_Delta']].sum())
BS_sensitivities = (BS_Duration_IRS, BS_Beta_S, BS_Delta_FX)

exec(','.join(Score['Source_of_crisis']) + '=' + ','.join(Score['Risk_bucket'].apply(lambda s:f'\'{s}\'')))

Delta_YTM = scenarios[Interest_rate].loc[0]
Delta_S = scenarios[Equity_market].loc[1]
Delta_FX = scenarios[International_economics].loc[2]

Delta_RF = (Delta_YTM, Delta_S, Delta_FX)

Capital_impact = pd.DataFrame({'BS_sensitivities':BS_sensitivities, 'Delta_RF':Delta_RF}, index = ['Interest_rate', 'Equity', 'FX'])
Capital_impact['1M_Impact'] = Capital_impact['BS_sensitivities']* Capital_impact['Delta_RF']/12
Capital_impact['Annualised'] = Capital_impact['1M_Impact']*12

Impact_1M = Capital_impact['1M_Impact'].sum()
Impact_Annualised = Capital_impact['Annualised'].sum()


rename_columns = {"BS_line_item": "Line Item", "BS_amount": "Outstanding($ Mn.)"}
BS_display = balance_sheet[balance_sheet['Date']==reporting_date][['BS_line_item','BS_amount']].rename(columns = rename_columns)
BS_display['Outstanding($ Mn.)'] = BS_display['Outstanding($ Mn.)'].astype(float)
liability = BS_display[balance_sheet['BS_component']=="Liability"]
liability.reset_index(drop=True, inplace=True)
asset = BS_display[balance_sheet['BS_component']=="Asset"]
asset.reset_index(drop=True, inplace=True)
offBS = BS_display[balance_sheet['BS_component']=="OffBS"]
offBS.reset_index(drop=True, inplace=True)




import intro
import risk_position
import liquidity_impact
import capital_impact
import report
import settings


PAGES = {
    "Balance Sheet": intro,
    "Risk Position": risk_position,
    "Liquidity Impact": liquidity_impact,
    "Capital Impact": capital_impact, 
    "Share Report":report,
    "Settings":settings
}
st.sidebar.title('Sequence')
selection = st.sidebar.radio("Select", list(PAGES.keys()))
page = PAGES[selection]
page.app()


if (selection == "Balance Sheet"):
    
    text = f"You are assessing balance sheet, risk position, liquidity projections and capital projections ** as at {reporting_date}**."
    st.markdown(text)
    
    
    
    
    # liability.reset_index('Line Item')
   
    total_liabilities = liability['Outstanding($ Mn.)'].sum()
    text = f"Below given is the **liability profile**. Total liabilities: **USD {total_liabilities:,.2f} million**."
    st.markdown(text)
    if not st.checkbox("Hide liability profile", True, key = '1'):  
        st.table(liability.style.format({'Outstanding($ Mn.)':"{:,.1f}"}).background_gradient(cmap=cm))
    
    
    total_assets = asset['Outstanding($ Mn.)'].sum()
    text = f"Below given is the **asset profile**. Total assets: **USD {total_assets:,.2f} million**."
    st.markdown(text)    
    if not st.checkbox("Hide asset profile", True, key = '2'):  
        st.table(asset.style.format({'Outstanding($ Mn.)':"{:,.1f}"}).background_gradient(cmap=cm))
    
    
    total_offBS = offBS['Outstanding($ Mn.)'].sum()
    text = f"Below given is the details of **contingent liabilities**. Total exposure: **USD {total_offBS:,.2f} million**."
    st.markdown(text)    
    if not st.checkbox("Hide contingent liability profile", True, key = '3'):  
        st.table(offBS.style.format({'Outstanding($ Mn.)':"{:,.1f}"}).background_gradient(cmap=cm))
    
    st.sidebar.header("Analyse")
    if not st.sidebar.checkbox("Hide", True, key = '4'):
         st.subheader("Ratio analysis")
         st.write("Coming soon...")
    
if (selection == "Risk Position"):
    
    bank_risk_score = Score['Score_sum'].mean()
    if bank_risk_score <= 3.33:
        bank_risk_level = "Low"
    elif bank_risk_score <= 6.67:
        bank_risk_level = "Medium"
    else:
        bank_risk_level = "High"
        
    text = f"**At {reporting_date}**, overall risk level of the Bank was **`{bank_risk_level}`**"
    st.markdown(text)
    
    #RAG status plot 
    bars = alt.Chart(Score).mark_bar().encode(
        alt.X('Score_sum' , title = "Risk levels (L | M | H)"),
        alt.Y('Source_of_crisis', title = "Sources of risk")
    ).properties(height = 300)
    
    st.altair_chart(bars, use_container_width=True)
    
    st.sidebar.subheader("Trend analysis")
    if not st.sidebar.checkbox("Hide", True, key = '5'):
         st.subheader("Last 12 months")
         st.write("Coming soon...")
    st.markdown("It can be noted that some items have low score while some have high. Accordingly, thise risk-causing factors are divided as `Low`, `Medium` and `High` impactful events. Those causes will have varied impact on various balance sheet line items. It is assumed that these causes will be in effect for next 30 days.")
    st.sidebar.subheader("Attribute analysis")
    if not st.sidebar.checkbox("Hide", True, key = '6'):
         st.subheader("Top 3 attributes")
         st.write("Coming soon...")
    
if (selection == "Liquidity Impact"):
    # st.write(asset)
    # cash = asset['Outstanding($ Mn.)'].loc[0].sum()
    cash_opening = asset[asset['Line Item']=='Cash']['Outstanding($ Mn.)'].sum()
    cash_sources = cash_forecast[cash_forecast['Source_usage']=='Source']['Cashflow_amount'].sum()
    cash_usages = cash_forecast[cash_forecast['Source_usage']=='Usage']['Cashflow_amount'].sum()
    cash_closing = cash_opening + cash_sources - cash_usages
    cash_position = pd.DataFrame({"": ('Opening cash', 'Sources of cash', 'Usages of cash', 'Closing cash'), "Amount ($ Mn.)": (cash_opening, cash_sources, cash_usages, cash_closing)})
    # st.table(cash_position)
    st.table(cash_position.style.format({'Amount ($ Mn.)':"{:,.1f}"}))
    st.sidebar.subheader("Attribute Analysis")
    if not st.sidebar.checkbox("Hide", True, key = '7'):
         st.subheader("Attribute analysis")
         st.write("Attribute analysis tells about the root-causes behind these cash source / usages and split between contractual, behavioural and other reasons")
         st.write("Coming soon...")
         
    st.sidebar.subheader("Trend Analysis")
    if not st.sidebar.checkbox("Hide", True, key = '8'):
         st.subheader("Trend analysis")
         st.write("Coming soon...")

if (selection == "Capital Impact"):
    st.table(Capital_impact)
    st.markdown(f"Capital impact due to `valuation loss` will be USD {Impact_1M: .1f} million, annualised, USD {Impact_Annualised: .1f} million.")
    st.sidebar.subheader("Attribute Analysis")
    if not st.sidebar.checkbox("Hide", True, key = '7'):
         st.subheader("Attribute analysis")
         st.write("Attribute analysis tells about the root-causes behind these cash source / usages and split between contractual, behavioural and other reasons")
         st.write("Coming soon...")
         
    st.sidebar.subheader("Trend Analysis")
    if not st.sidebar.checkbox("Hide", True, key = '8'):
         st.subheader("Trend analysis")
         st.write("Coming soon...")
# st.dataframe(Capital_impact)
# st.write(Impact_1M, Impact_Annualised)