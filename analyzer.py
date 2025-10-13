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
