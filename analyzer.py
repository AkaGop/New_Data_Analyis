# analyzer.py

from datetime import datetime
import pandas as pd

def calculate_takt_times(events: list, start_index: int, end_index: int) -> pd.DataFrame:
    """
    Calculates the Takt time (cycle time) between each panel processing event.
    
    Args:
        events: The full list of parsed events.
        start_index: The list index of the LOADSTART event.
        end_index: The list index of the completion event.

    Returns:
        A pandas DataFrame with panel numbers and their individual cycle times.
    """
    # Find all "LoadedToTool" events within the bounds of the job
    load_events = [
        e for e in events[start_index:end_index] 
        if e.get('details', {}).get('CEID') == 127
    ]

    if len(load_events) < 2:
        return pd.DataFrame() # Not enough data to calculate intervals

    timestamps = [datetime.strptime(e['timestamp'], "%Y/%m/%d %H:%M:%S.%f") for e in load_events]
    
    # Calculate the time difference in seconds between each consecutive event
    deltas = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]

    # Create a DataFrame for easy plotting
    takt_df = pd.DataFrame({
        'Panel #': range(2, len(timestamps) + 1), # Start from Panel 2
        'Cycle Time (sec)': deltas
    })
    
    return takt_df

def analyze_data(events: list) -> dict:
    """
    Analyzes a list of parsed events to calculate high-level KPIs and Takt times.
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
        "takt_times_df": pd.DataFrame() # Add a placeholder for the Takt time data
    }

    if not events:
        return summary

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
                
                # --- NEW: Call the Takt Time calculation function ---
                summary['takt_times_df'] = calculate_takt_times(events, start_index, end_index)

            except (ValueError, TypeError):
                summary['job_status'] = "Time Calculation Error"

    # Aggregate other data
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        if str(details.get('Result', '')).startswith("Failure"):
            summary['anomalies'].append(f"{event['timestamp']}: Host command failed.")
        if details.get('AlarmID'):
            summary['alarms'].append(f"{event['timestamp']}: Alarm {details['AlarmID']} occurred.")
            
    return summary
