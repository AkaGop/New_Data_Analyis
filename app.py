a_# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

with st.sidebar:
    st.title("🤖 Log Analyzer")
    uploaded_file = st.file_uploader("Upload Hirata Log File", type=['txt', 'log'])
    st.info("This tool provides engineering analysis of Hirata SECS/GEM logs.")

if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events)
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)

    st.header("Job Performance Dashboard")
    st.markdown("---")

    # --- START OF HIGHLIGHTED CHANGE ---
    # The number of columns is changed from 5 to 4.
    # The "Job Status" metric has been removed.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lot ID", str(summary.get('lot_id', 'N/A')))
    c2.metric("Total Panels", int(summary.get('panel_count', 0)))
    c3.metric("Job Duration (sec)", f"{summary.get('total_duration(sec)', 0.0):.2f}")
    c4.metric("Avg Cycle Time (sec)", f"{summary.get('avg_cycle_time(sec)', 0.0):.2f}")
    # --- END OF HIGHLIGHTED CHANGE ---
    
    with st.expander("Show Data Analysis"):
        st.subheader("Event Frequency")
        if not eda_results.get('event_counts', pd.Series()).empty:
            st.bar_chart(eda_results['event_counts'])
        else:
            st.info("No events to analyze for frequency.")

        st.subheader("Alarm Analysis")
        if not eda_results.get('alarm_table', pd.DataFrame()).empty:
            st.write("Alarm Counts:")
            st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:")
            st.dataframe(eda_results['alarm_table'], use_container_width=True)
        else:
            st.success("✅ No Alarms Found in Log")

    st.header("Detailed Event Log")
    if not df.empty:
        cols = ["timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount", "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"]
        display_cols = [col for col in cols if col in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
    else:
        st.warning("No meaningful events were found.")
else:
    st.title("Welcome")
    st.info("⬅️ Please upload a log file to begin analysis.")
