# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP

st.set_page_config(page_title="Hirata Log Analyzer - Parser Test", layout="wide")
st.title("Hirata Equipment Log Analyzer - Step 2: Parser Validation")

uploaded_file = st.file_uploader("Upload your Hirata Log File (.txt or .log)", type=['txt', 'log'])

if uploaded_file:
    with st.spinner("Parsing log file..."):
        parsed_events = parse_log_file(uploaded_file)
    
    st.header("Parser Output")

    if parsed_events:
        st.metric(label="Meaningful Events Found", value=len(parsed_events))
        
        # We will use json_normalize which is great for nested data
        df = pd.json_normalize(parsed_events)
        
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        elif 'details.RCMD' in df.columns:
            df['EventName'] = df['details.RCMD']
        else:
            df['EventName'] = "N/A"

        # Display all available columns
        st.dataframe(df)

        with st.expander("Show Raw JSON Output"):
            st.json(parsed_events)
    else:
        st.warning("No meaningful events were found in the log file.")
else:
    st.info("Please upload a log file to begin analysis.")
