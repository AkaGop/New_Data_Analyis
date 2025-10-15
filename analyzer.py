# analyzer.py
from datetime import datetime
import pandas as pd

# The perform_eda function is correct and does not need changes.
def perform_eda(df: pd.DataFrame) -> dict:
    # ... (code remains the same) ...

def analyze_data(events: list) -> dict:
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A", "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0, "job_status": "No Job Found",
    }
    if not events: return summary

    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    
    if start_event:
        # --- START OF HIGHLIGHTED FIX ---
        
        # Rule 1: Prioritize LotID from the LOADSTART command.
        lot_id = start_event['details'].get('LotID', 'N/A')
        
        # Rule 2: If LotID is missing from LOADSTART, search the rest of the log for it.
        if lot_id == 'N/A' or not lot_id:
            found_lot_id = next((e['details'].get('LotID') for e in events if e.get('details', {}).get('LotID')), 'N/A')
            summary['lot_id'] = found_lot_id
        else:
            summary['lot_id'] = lot_id

        # --- END OF HIGHLIGHTED FIX ---

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
    else:
        panel_activity_found = any(e.get('details', {}).get('CEID') in [120, 127] for e in events)
        if panel_activity_found:
            summary['lot_id'] = "Dummy/Test Panels"

    # Aggregate summary data
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
            
    return summary
