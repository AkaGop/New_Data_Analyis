# analyzer.py
from datetime import datetime
import pandas as pd

def analyze_data(events: list) -> dict:
    """
    Final, enhanced analyzer. Tracks job KPIs and control state changes.
    """
    summary = {
        "operators": set(),
        "magazines": set(),
        "lot_id": "N/A",
        "panel_count": 0,
        "job_start_time": "N/A",
        "job_end_time": "N/A",
        "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0,
        "anomalies": [],
        "alarms": [],
        "job_status": "No Job Found",
        "takt_times_df": pd.DataFrame(),
        "control_state_changes": [] # --- NEW: To store state change events ---
    }

    if not events:
        return summary

    # --- Find Job Cycle (logic is correct) ---
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

    # --- Aggregate all other data across the entire log ---
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        if str(details.get('Result', '')).startswith("Failure"):
            summary['anomalies'].append(f"{event['timestamp']}: Host command failed.")
        if details.get('AlarmID'):
            summary['alarms'].append(f"{event['timestamp']}: Alarm {details['AlarmID']} occurred.")
        
        # --- NEW: Logic to find and record control state changes ---
        ceid = details.get('CEID')
        if ceid == 12: # GemControlStateLOCAL
            summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "LOCAL"})
        elif ceid == 13: # GemControlStateREMOTE
            summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "REMOTE"})

    # --- NEW: Logic to apply default Lot ID if none was found ---
    if summary['lot_id'] == "N/A" and summary['job_status'] == "No Job Found":
        summary['lot_id'] = "Test Lot"
            
    return summary
