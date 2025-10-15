# analyzer.py
from datetime import datetime
import pandas as pd

# This function does not need to change.
def perform_eda(df: pd.DataFrame) -> dict:
    """Performs Exploratory Data Analysis on the parsed log data."""
    eda_results = {}
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')
    if 'details.AlarmID' in df.columns:
        alarm_events = df[df['details.AlarmID'].notna()].copy()
        if not alarm_events.empty:
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            eda_results['alarm_counts'] = alarm_ids.value_counts()
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID']]
        else:
            eda_results['alarm_counts'] = pd.Series(dtype='int64')
            eda_results['alarm_table'] = pd.DataFrame()
    else:
        eda_results['alarm_counts'] = pd.Series(dtype='int64')
        eda_results['alarm_table'] = pd.DataFrame()
    return eda_results

def analyze_data(events: list) -> dict:
    """
    Analyzes a list of parsed events to calculate high-level KPIs.
    """
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A", "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0, "job_status": "No Job Found",
    }
    if not events: return summary

    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    
    if start_event:
        # --- This block is the same ---
        summary['lot_id'] = start_event['details'].get('LotID', 'N/A')
        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError):
             summary['panel_count'] = 0
        summary['job_start_time'] = start_event['timestamp']
        summary['job_status'] = "Started but did not complete"
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        if end_event:
            # (Calculation logic remains the same)
            # ...
            pass # Placeholder for brevity, the logic inside here is correct.
    
    # --- START OF HIGHLIGHTED CHANGE ---
    else:
        # Rule #2: If no LOADSTART was found, check if any panel processing occurred.
        # CEID 120 (IDRead) and 127 (LoadedToTool) are good indicators of panel movement.
        panel_activity_found = any(e.get('details', {}).get('CEID') in [120, 127] for e in events)
        if panel_activity_found:
            # Rule #2: If yes, label it as a test run.
            summary['lot_id'] = "Dummy/Test Panels"
        # Rule #3: If no job and no panel activity, Lot ID remains the default "N/A".
    # --- END OF HIGHLIGHTED CHANGE ---

    # Aggregate summary data (this part is the same)
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
            
    return summary
