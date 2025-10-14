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
    
    # --- KPI Dashboard ---
    st.header("Job Performance Dashboard")
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Job Status", summary['job_status'])
    col2.metric("Lot ID", str(summary['lot_id']))
    col3.metric("Total Panels in Job", int(summary['panel_count']))
    col4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")

    # --- NEW: Dynamic Log Summary Section ---
    st.header("Overall Log Summary")
    st.markdown("---")
    
    colA, colB, colC = st.columns(3)
    # Use list comprehension to create formatted strings from the sets
    colA.multiselect("Operators Found", options=list(summary['operators']), default=list(summary['operators']))
    colB.multiselect("Magazines Found", options=list(summary['magazines']), default=list(summary['magazines']))
    
    with colC:
        st.subheader("Alarms & Anomalies")
        if not summary['alarms'] and not summary['anomalies']:
            st.success("No Alarms or Anomalies Found")
        else:
            for alarm in summary['alarms']:
                st.warning(alarm)
            for anomaly in summary['anomalies']:
                st.error(anomaly)

    st.write("---")

    # --- Detailed Log Table ---
    st.header("Detailed Event Log")
    if parsed_events:
        df = pd.json_normalize(parsed_events)
        
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown Event")
        if 'details.RCMD' in df.columns:
            df.rename(columns={'details.RCMD': 'EventName_RCMD'}, inplace=True)
            if 'EventName' in df.columns:
                df['EventName'].fillna(df['EventName_RCMD'], inplace=True)
            else:
                df['EventName'] = df['EventName_RCMD']
        
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
