# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data

st.set_page_config(page_title="Hirata Log Analyzer", page_icon="🤖", layout="wide")

# --- Sidebar (unchanged) ---
with st.sidebar:
    st.title("🤖 Hirata Log Analyzer")
    # ... (rest of sidebar code is unchanged) ...

# --- Main Page ---
if uploaded_file:
    # ... (parsing logic is unchanged) ...
    
    # --- START OF HIGHLIGHTED CHANGE ---
    # Updated KPI Dashboard Layout
    st.header("Job Performance Dashboard")
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Control State", summary['control_state'])
    col2.metric("Lot ID", str(summary['lot_id']))
    col3.metric("Total Panels", summary['panel_count'])
    col4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    col5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")
    # --- END OF HIGHLIGHTED CHANGE ---

    # ... (the rest of the app display logic is unchanged) ...

else:
    st.title("Welcome to the Hirata Log Analyzer")
    st.info("⬅️ Please upload a log file using the sidebar to begin.")
