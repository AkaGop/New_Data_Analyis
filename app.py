# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

uploaded_file = st.file_uploader("Upload your Hirata Log File (.txt or .log)", type=['txt', 'log'])

if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        summary = analyze_data(parsed_events)
    
    # --- The Dashboard ---
    st.header("Job Performance Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Job Status", summary['job_status'])
    col2.metric("Lot ID", str(summary['lot_id']))
    col3.metric("Total Panels", summary['panel_count'])
    col4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")
    
    st.write("---")

    # --- The Detailed Log Table ---
    st.header("Detailed Event Log")
    if parsed_events:
        df = pd.json_normalize(parsed_events)
        
        # Create a human-readable 'EventName' column
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown Event")
        
        if 'details.RCMD' in df.columns:
            # Fill in names for S2F49 commands where EventName might be empty
            df['EventName'].fillna(df['details.RCMD'], inplace=True)
        
        # Define and display columns in a logical order
        cols_in_order = [
            "timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount",
            "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus",
            "details.AlarmID"
        ]
        display_cols = [col for col in cols_in_order if col in df.columns]
        st.dataframe(df[display_cols])

        with st.expander("Show Raw JSON Data (for debugging)"):
            st.json(parsed_events)
    else:
        st.warning("No meaningful events were found in the log file.")
else:
    st.info("Please upload a log file to begin analysis.")
