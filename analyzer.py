# analyzer.py
from datetime import datetime
import pandas as pd

def calculate_takt_times(events: list, start_index: int, end_index: int) -> pd.DataFrame:
    """Calculates the Takt time between each panel processing event."""
    # This function is now more flexible, looking for either load or unload events.
    load_events = [e for e in events[start_index:end_index] if e.get('details', {}).get('CEID') == 127] # LoadedToTool
    unload_events = [e for e in events[start_index:end_index] if e.get('details', {}).get('CEID') == 121] # UnloadedFromTool (example)

    # Prioritize load events as they are more common for takt time
    panel_events = load_events if len(load_events) > 1 else unload_events

    if len(panel_events) < 2:
        return pd.DataFrame()

    timestamps = [datetime.strptime(e['timestamp'], "%Y/%m/%d %H:%M:%S.%f") for e in panel_events]
    deltas = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
    
    takt_df = pd.DataFrame({
        'Panel #': range(2, len(timestamps) + 1),
        'Cycle Time (sec)': deltas
    })
    return takt_df

def analyze_data(events: list) -> dict:
    """
    Final, robust analyzer. It finds the first complete job (Load or Unload) in the log.
    """
    summary = {
        "job_status": "No Job Found", "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A",
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
        "operators": set(), "magazines": set(), "anomalies": [], "alarms": [],
        "takt_times_df": pd.DataFrame()
    }
    if not events: return summary

    # --- START OF HIGHLIGHTED FIX ---
    # Step 1: Find the first job-starting command, either LOADSTART or UNLOADSTART.
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') in ['LOADSTART', 'UNLOADSTART']), None)
    
    if start_event:
        summary['lot_id'] = start_event['details'].get('LotID', 'N/A')
        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError):
             summary['panel_count'] = 0
        summary['job_start_time'] = start_event['timestamp']
        summary['job_status'] = "Started but did not complete"
        start_index = events.index(start_event)
        
        # Step 2: Look for a corresponding completion event AFTER the start event.
        # CEID 131 = LoadToToolCompleted, CEID 132 = UnloadFromToolCompleted
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        
        if end_event:
            end_index = events.index(end_event)
            summary['job_end_time'] = end_event['timestamp']
            summary['job_status'] = "Completed"
            
            try:
                t_start = datetime.strptime(summary['job_start_time'], "%Y/%m/%d %H:%M:%S.%f")
                t_end = datetime.strptime(summary['job_end_time'], "%Y/%m/%d %H:%M:%S.%f")
                duration = (t_end - t_start).total_seconds()
                if duration >= 0:
                    summary['total_duration_sec'] = round(duration, 2)
                    if summary['panel_count'] > 0:
                        summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)
                summary['takt_times_df'] = calculate_takt_times(events, start_index, end_index)
            except (ValueError, TypeError):
                summary['job_status'] = "Time Calculation Error"
    # --- END OF HIGHLIGHTED FIX ---

    # Aggregate other data (this part is correct)
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        if str(details.get('Result', '')).startswith("Failure"):
            summary['anomalies'].append(f"{event['timestamp']}: Host command failed.")
        if details.get('AlarmID'):
            summary['alarms'].append(f"{event['timestamp']}: Alarm {details['AlarmID']} occurred.")
            
    return summary
