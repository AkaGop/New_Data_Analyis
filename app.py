# app.py

import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data

st.set_page_config(
    page_title="Hirata Log Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 Hirata Log Analyzer")
    uploaded_file = st.file_uploader("Upload Log File", type=['txt', 'log'])
    st.write("---")
    st.header("About")
    st.info(
        "This tool provides engineering analysis of Hirata SECS/GEM logs, "
        "focusing on job performance, equipment states, and anomalies."
    )
    with st.expander("Metric Definitions"):
        st.markdown("""
        *   **Lot ID:** The unique ID for the batch of material. Defaults to 'Test Lot' if no production job is found.
        *   **Total Panels:** The number of panels specified in the `LOADSTART` command.
        *   **Job Duration:** Total time from `LOADSTART` to job completion.
        *   **Avg Cycle Time:** The average time to process a single panel during the job.
        *   **Control State Changes:** A log of when the equipment was switched between Host control (REMOTE) and operator control (LOCAL).
        """)

# --- Main Page ---
if uploaded_file:
    with st.spinner("Analyzing log file..."):
        parsed_events = parse_log_file(uploaded_file)
        summary = analyze_data(parsed_events)

    # --- KPI Dashboard (Now 4 columns) ---
    st.header("Job Performance Dashboard")
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lot ID", str(summary['lot_id']))
    col2.metric("Total Panels in Job", summary['panel_count'])
    col3.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col4.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")

    # --- Overall Log Summary ---
    st.header("Overall Log Summary")
    st.markdown("---")
    colA, colB, colC, colD = st.columns([1, 1, 1, 2]) # Added a 4th column for state changes
    
    with colA:
        st.subheader("Operators")
        st.dataframe(pd.DataFrame(list(summary['operators']), columns=["ID"]), hide_index=True, use_container_width=True)
    with colB:
        st.subheader("Magazines")
        st.dataframe(pd.DataFrame(list(summary['magazines']), columns=["ID"]), hide_index=True, use_container_width=True)
    with colC:
        st.subheader("State Changes")
        if summary['control_state_changes']:
            st.dataframe(pd.DataFrame(summary['control_state_changes']), hide_index=True, use_container_width=True)
        else:
            st.info("No Local/Remote changes detected.")
    with colD:
        st.subheader("Alarms & Anomalies")
        if not summary['alarms'] and not summary['anomalies']:
            st.success("✅ No Alarms or Anomalies Found")
        else:
            for alarm in summary['alarms']: st.warning(f"⚠️ {alarm}")
            for anomaly in summary['anomalies']: st.error(f"❌ {anomaly}")

    st.write("---")
    # ... (Rest of the app remains the same) ...
    
else:
    st.title("Welcome to the Hirata Log Analyzer")
    st.info("⬅️ Please upload a log file using the sidebar to begin.")
