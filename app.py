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
    
    uploaded_file = st.file_uploader(
        "Upload your Hirata Log File (.txt or .log)",
        type=['txt', 'log']
    )

    st.write("---")

    # --- NEW: Explanations Section ---
    st.header("About This App")
    st.info(
        "This application analyzes Hirata equipment log files to provide actionable "
        "engineering insights into job performance and equipment reliability."
    )

    with st.expander("Metric Definitions"):
        st.markdown("""
        *   **Job Status:** Indicates if a `LOADSTART` or `UNLOADSTART` job was found and completed within the log file.
        *   **Lot ID:** The unique identifier for the batch of material being processed.
        *   **Total Panels:** The number of panels specified in the job command.
        *   **Job Duration:** The total time from the job start command to the job completion event.
        *   **Avg Cycle Time:** The `Job Duration` divided by `Total Panels`. A high-level indicator of overall performance.
        *   **Takt Time / Cycle Time:** The specific time taken to process a single panel (e.g., the time between `LoadedToTool` event #1 and #2). A rising Takt Time is a key indicator of a bottleneck.
        *   **Std. Deviation:** A measure of the consistency of the Takt Time. A low number means the process is stable; a high number indicates erratic performance.
        """)

# --- Main Page Display ---
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
    col3.metric("Total Panels", summary['panel_count'])
    col4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")

    # --- Takt Time Analysis Section ---
    if not summary['takt_times_df'].empty:
        st.header("Panel-by-Panel Takt Time Analysis")
        st.markdown("---")
        
        takt_df = summary['takt_times_df']
        
        st.subheader("Cycle Time per Panel")
        st.line_chart(takt_df.set_index('Panel #'))
        
        st.subheader("Takt Time Statistics")
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        col_stats1.metric("Min Cycle Time (sec)", f"{takt_df['Cycle Time (sec)'].min():.2f}")
        col_stats2.metric("Max Cycle Time (sec)", f"{takt_df['Cycle Time (sec)'].max():.2f}")
        col_stats3.metric("Std. Deviation", f"{takt_df['Cycle Time (sec)'].std():.2f}")

    # ... (Rest of the app remains the same) ...
    st.write("---")
    st.header("Detailed Event Log")
    if parsed_events:
        df = pd.json_normalize(parsed_events)
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown Event")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
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
