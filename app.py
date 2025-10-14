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
    
    st.header("Job Performance Dashboard")
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lot ID", str(summary.get('lot_id', 'N/A')))
    col2.metric("Total Panels in Job", int(summary.get('panel_count', 0)))
    col3.metric("Job Duration (sec)", f"{summary.get('total_duration_sec', 0.0):.2f}")
    col4.metric("Avg Cycle Time (sec)", f"{summary.get('avg_cycle_time_sec', 0.0):.2f}")

    st.header("Overall Log Summary")
    st.markdown("---")
    colA, colB, colC, colD = st.columns([1, 1, 1, 2])
    
    with colA:
        st.subheader("Operators")
        st.dataframe(pd.DataFrame(list(summary.get('operators', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    with colB:
        st.subheader("Magazines")
        st.dataframe(pd.DataFrame(list(summary.get('magazines', [])), columns=["ID"]), hide_index=True, use_container_width=True)
    
    # --- START OF HIGHLIGHTED FIX ---
    with colC:
        st.subheader("State Changes")
        # Use .get() for safety. It returns an empty list if the key is missing.
        state_changes = summary.get('control_state_changes', [])
        if state_changes:
            st.dataframe(pd.DataFrame(state_changes), hide_index=True, use_container_width=True)
        else:
            st.info("No Local/Remote changes detected.")
    # --- END OF HIGHLIGHTED FIX ---
            
    with colD:
        st.subheader("Alarms & Anomalies")
        alarms = summary.get('alarms', [])
        anomalies = summary.get('anomalies', [])
        if not alarms and not anomalies:
            st.success("✅ No Alarms or Anomalies Found")
        else:
            for alarm in alarms: st.warning(f"⚠️ {alarm}")
            for anomaly in anomalies: st.error(f"❌ {anomaly}")

    st.write("---")
    st.header("Detailed Event Log")
    if parsed_events:
        df = pd.json_normalize(parsed_events)
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        cols = ["timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount", "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"]
        display_cols = [col for col in cols if col in df.columns]
        st.dataframe(df[display_cols])
        with st.expander("Show Raw JSON Data"): st.json(parsed_events)
    else:
        st.warning("No meaningful events were found.")
else:
    st.info("Please upload a log file to begin analysis.")
