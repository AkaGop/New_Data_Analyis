# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data

# --- Page Configuration (Best practice: do this first) ---
st.set_page_config(
    page_title="Hirata Log Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- Sidebar for Inputs ---
with st.sidebar:
    st.title("Hirata Log Analyzer")
    st.write("---")
    uploaded_file = st.file_uploader(
        "Upload your Hirata Log File (.txt or .log)",
        type=['txt', 'log']
    )
    st.info("This app parses Hirata SECS/GEM logs to extract KPIs and event data.")

# --- Main Page Display ---
if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        summary = analyze_data(parsed_events)

    st.header("Job Performance Dashboard")
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Job Status", summary['job_status'])
    col2.metric("Lot ID", str(summary['lot_id']))
    col3.metric("Total Panels in Job", int(summary['panel_count']))
    col4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")

    st.header("Overall Log Summary")
    st.markdown("---")
    
    colA, colB, colC = st.columns([1, 1, 2]) # Give more space to the anomalies column
    
    with colA:
        st.subheader("Operators Found")
        if summary['operators']:
            st.dataframe(pd.DataFrame(list(summary['operators']), columns=["Operator ID"]), use_container_width=True)
        else:
            st.info("No operator IDs found.")

    with colB:
        st.subheader("Magazines Found")
        if summary['magazines']:
            st.dataframe(pd.DataFrame(list(summary['magazines']), columns=["Magazine ID"]), use_container_width=True)
        else:
            st.info("No magazine IDs found.")

    with colC:
        st.subheader("Alarms & Anomalies")
        if not summary['alarms'] and not summary['anomalies']:
            st.success("✅ No Alarms or Anomalies Found")
        else:
            for alarm in summary['alarms']:
                st.warning(f"⚠️ {alarm}")
            for anomaly in summary['anomalies']:
                st.error(f"❌ {anomaly}")

    st.write("---")

    st.header("Detailed Event Log")
    if parsed_events:
        df = pd.json_normalize(parsed_events)
        
        # Create a human-readable 'EventName' column
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown Event")
        
        if 'details.RCMD' in df.columns:
            # Use .loc to safely fill in names for S2F49 commands where EventName is still empty
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
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
    st.title("Welcome to the Hirata Log Analyzer")
    st.info("⬅️ Please upload a log file using the sidebar to begin.")
