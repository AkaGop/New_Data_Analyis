# analyzer.py
from datetime import datetime
import pandas as pd

def perform_eda(df: pd.DataFrame) -> dict:
    """
    A robust EDA function that defensively checks for the existence of columns.
    """
    eda_results = {}

    # --- START OF HIGHLIGHTED FIX ---

    # Event Frequency Analysis (Defensive Check)
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')

    # Alarm Analysis (Defensive Check)
    if 'details.AlarmID' in df.columns:
        alarm_events = df[df['details.AlarmID'].notna()].copy() # Use .copy() to avoid SettingWithCopyWarning
        if not alarm_events.empty:
            # Coerce to numeric, errors will become NaN which are then dropped
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            eda_results['alarm_counts'] = alarm_ids.value_counts()
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID']]
        else:
            eda_results['alarm_counts'] = pd.Series(dtype='int64')
            eda_results['alarm_table'] = pd.DataFrame()
    else:
        # If the column doesn't even exist, return empty results.
        eda_results['alarm_counts'] = pd.Series(dtype='int64')
        eda_results['alarm_table'] = pd.DataFrame()
        
    # --- END OF HIGHLIGHTED FIX ---
        
    return eda_results

def analyze_data(events: list) -> dict:
    """Analyzes a list of parsed events to calculate high-level KPIs."""
    summary = {
        "job_status": "No Job Found", "lot_id": "N/A", "panel_count": 0,
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
    }

    # This part of the logic is sound and does not need to change.
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    if start_event:
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
            summary['job_status'] = "Completed"
            try:
                t_start = datetime.strptime(start_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                t_end = datetime.strptime(end_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                duration = (t_end - t_start).total_seconds()
                if duration >= 0:
                    summary['total_duration_sec'] = round(duration, 2)
                    if summary['panel_count'] > 0:
                        summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)
            except (ValueError, TypeError):
                summary['job_status'] = "Time Calculation Error"

    if summary['job_status'] == "No Job Found":
        summary['lot_id'] = "Test Lot / No Job"
            
    return summary
