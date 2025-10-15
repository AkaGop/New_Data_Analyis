# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP, ALARM_CODE_MAP # Import ALARM_CODE_MAP here too
from analyzer import analyze_data, perform_eda

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

# --- Sidebar (No Changes) ---

# --- Main Page ---
if uploaded_file:
    # ... (Parsing and Summary logic is the same) ...

    # --- START OF HIGHLIGHTED CHANGE ---
    # We will also add the AlarmText to the main detailed log.
    st.header("Detailed Event Log")
    if not df.empty:
        # Add AlarmText column if alarms are present
        if 'details.AlarmID' in df.columns:
            # Use .loc to safely create the new column
            df.loc[:, 'AlarmText'] = pd.to_numeric(df['details.AlarmID'], errors='coerce').map(ALARM_CODE_MAP)

        cols_in_order = [
            "timestamp", "msg_name", "EventName", "AlarmText", "details.LotID", "details.PanelCount",
            "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"
        ]
        display_cols = [col for col in cols_in_order if col in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
