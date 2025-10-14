# analyzer.py
from datetime import datetime

def analyze_data(events: list) -> dict:
    summary = {
        "control_state": "Unknown", "lot_id": "N/A", "panel_count": 0,
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
    }
    # Find the last known control state
    for event in reversed(events):
        if event.get('details', {}).get('ControlState'):
            state_val = event['details']['ControlState']
            if state_val == '4': summary['control_state'] = 'Online Local'
            elif state_val == '5': summary['control_state'] = 'Remote'
            break
    
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') in ['LOADSTART', 'UNLOADSTART']), None)
    if start_event:
        lot_id = start_event['details'].get('LotID', '').strip()
        summary['lot_id'] = lot_id if lot_id else "Test / Dummy Lot"
        summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        
        if end_event:
            try:
                t_start = datetime.strptime(start_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                t_end = datetime.strptime(end_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                duration = (t_end - t_start).total_seconds()
                if duration >= 0:
                    summary['total_duration_sec'] = round(duration, 2)
                    if summary['panel_count'] > 0:
                        summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)
            except (ValueError, TypeError): pass
    return summary```

**4. `app.py` (Final, Validated UI)**

```python
# app.py
import streamlit as st
import pandas as pd
from log_parser import parse_log_file
from config import CEID_MAP
from analyzer import analyze_data

st.set_page_config(page_title="Hirata Log Analyzer", layout="wide")
st.title("Hirata Equipment Log Analyzer")

# --- Sidebar ---
with st.sidebar:
    st.header("Upload Log File")
    uploaded_file = st.file_uploader("Select a .txt or .log file", type=['txt', 'log'])

# --- Main Page ---
if uploaded_file:
    with st.spinner("Analyzing log file..."):
        events = parse_log_file(uploaded_file)
        summary = analyze_data(events)
    
    st.header("Job Performance Dashboard")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Control State", summary['control_state'])
    c2.metric("Lot ID", str(summary['lot_id']))
    c3.metric("Total Panels", int(summary['panel_count']))
    c4.metric("Job Duration (sec)", f"{summary['total_duration_sec']:.2f}")
    c5.metric("Avg Cycle Time (sec)", f"{summary['avg_cycle_time_sec']:.2f}")
    
    st.write("---")
    st.header("Detailed Event Log")
    
    if events:
        df = pd.json_normalize(events)
        if 'details.CEID' in df.columns:
            df['EventName'] = pd.to_numeric(df['details.CEID'], errors='coerce').map(CEID_MAP).fillna("Unknown")
        if 'details.RCMD' in df.columns:
            df.loc[df['EventName'].isnull(), 'EventName'] = df['details.RCMD']
        
        cols = ["timestamp", "msg_name", "EventName", "details.LotID", "details.PanelCount", "details.MagazineID", "details.OperatorID", "details.PortID", "details.PortStatus", "details.AlarmID"]
        display_cols = [col for col in cols if col in df.columns]
        st.dataframe(df[display_cols])
        
        with st.expander("Show Raw JSON Data"): st.json(events)
    else:
        st.warning("No meaningful events were found.")
else:
    st.info("Please upload a file to begin analysis.")
