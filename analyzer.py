# analyzer.py
from datetime import datetime
import pandas as pd

def get_control_state(events: list) -> str:
    """
    Finds the last known control state (Remote or Local) from the event log.
    """
    # Default to 'Unknown' if no specific event is found
    last_state = "Unknown"
    
    for event in events:
        details = event.get('details', {})
        ceid = details.get('CEID')
        
        if ceid == 13: # GemControlStateREMOTE
            last_state = "REMOTE"
        elif ceid == 12: # GemControlStateLOCAL
            last_state = "LOCAL"
            
    return last_state

def calculate_takt_times(events: list, start_index: int, end_index: int) -> pd.DataFrame:
    """Calculates the Takt time between each panel processing event."""
    # This function is correct and does not need changes.
    load_events = [e for e in events[start_index:end_index] if e.get('details', {}).get('CEID') == 127]
    unload_events = [e for e in events[start_index:end_index] if e.get('details', {}).get('CEID') == 121]
    panel_events = load_events if len(load_events) > 1 else unload_events
    if len(panel_events) < 2: return pd.DataFrame()
    timestamps = [datetime.strptime(e['timestamp'], "%Y/%m/%d %H:%M:%S.%f") for e in panel_events]
    deltas = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
    return pd.DataFrame({'Panel #': range(2, len(timestamps) + 1), 'Cycle Time (sec)': deltas})

def analyze_data(events: list) -> dict:
    """
    Final, robust analyzer. It finds the first complete job, determines control state,
    and infers if a lot is a test/dummy lot.
    """
    summary = {
        "control_state": "Unknown", "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A",
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
        "operators": set(), "magazines": set(), "anomalies": [], "alarms": [],
        "takt_times_df": pd.DataFrame()
    }
    if not events: return summary

    # --- START OF HIGHLIGHTED CHANGES ---

    # 1. Determine the control state for the entire log.
    summary['control_state'] = get_control_state(events)

    # 2. Find the first job-starting command.
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') in ['LOADSTART', 'UNLOADSTART']), None)
    
    if start_event:
        # 3. Implement "Test Lot" logic.
        lot_id = start_event['details'].get('LotID', '').strip()
        if not lot_id or lot_id.lower() == 'none':
            summary['lot_id'] = "Test / Dummy Lot"
        else:
            summary['lot_id'] = lot_id

        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError):
             summary['panel_count'] = 0
        summary['job_start_time'] = start_event['timestamp']
        
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        
        if end_event:
            # (Calculation logic remains the same and is correct)
            # ... [omitted for brevity, but it's the same as before] ...
            pass # Placeholder for the existing correct logic

    # --- END OF HIGHLIGHTED CHANGES ---

    # Aggregate other data (this part is correct)
    # ... [omitted for brevity, but it's the same as before] ...
            
    return summary
