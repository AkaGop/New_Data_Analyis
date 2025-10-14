# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data, perform_eda # Import the new EDA function

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 Log Analyzer")
    uploaded_file = st.file_uploader("Upload Hirata Log File", type=['txt', 'log'])
    st.write("---")
    st.header("About")
    st.info("This tool provides engineering analysis of Hirata SECS/GEM logs.")

# --- Main Page ---
if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        df = pd.json_normalize(parsed_events) # Convert to DataFrame once
        
        # --- Data Enrichment ---
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            # Fill EventName for S2F49 messages
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        # Perform analyses
        summary = analyze_data(parsed_events)
        eda_results = perform_eda(df)

    # --- KPI Dashboard ---
    st.header("Job Performance Dashboard")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Job Status", summary['job_status'])
    c2.metric("Lot ID", str(summary['lot_id']))
    c3.metric("Total Panels in Job", summary['panel_count'])
    c4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")

    # --- NEW: Exploratory Data Analysis Section ---
    with st.expander("Show Exploratory Data Analysis (EDA)"):
        st.subheader("Event Frequency")
        if not eda_results['event_counts'].empty:
            st.bar_chart(eda_results['event_counts'])
        else:
            st.info("No events to analyze for frequency.")

        st.subheader("Alarm Analysis")
        if not eda_results['alarm_counts'].empty:
            st.bar_chart(eda_results['alarm_counts'])
            st.write("Alarm Events Log:")
            st.dataframe(eda_results['alarm_table'], use_container_width=True)
        else:
            st.success("✅ No Alarms Found in Log")

    # --- Detailed Log Table ---
    st.header("Detailed Event Log")
    cols_in_order = [
        "timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount",
        "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"
    ]
    display_cols = [col for col in cols_in_order if col in df.columns]
    st.dataframe(df[display_cols], hide_index=True)

else:
    st.title("Welcome")
    st.info("⬅️ Please upload a log file using the sidebar to begin analysis.")
