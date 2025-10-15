# analyzer.py
from datetime import datetime
import pandas as pd

def perform_eda(df: pd.DataFrame) -> dict:
    """
    A robust EDA function that defensively checks for the existence of columns.
    """
    eda_results = {}

    # Event Frequency Analysis (Defensive Check)
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')

    # Alarm Analysis (Defensive Check)
    if 'details.AlarmID' in df.columns:
        # Use .copy() to avoid SettingWithCopyWarning on older pandas versions
        alarm_events = df[df['details.AlarmID'].notna()].copy()
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
        
    return eda_results

def analyze_data(df: pd.DataFrame) -> dict:
    """Analyzes a dataframe of parsed events to calculate high-level KPIs."""
    summary = {
        "job_status": "No Job Found", "lot_id": "N/A", "panel_count": 0,
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
        "unique_alarms_count": 0, "alarms": []
    }
    
    if df.empty:
        return summary

    # Find the first LOADSTART event
    start_events = df[df['EventName'] == 'LOADSTART']
    if start_events.empty:
        summary['lot_id'] = "Test Lot / No Job"
        return summary
        
    first_start_event = start_events.iloc[0]
    summary['lot_id'] = first_start_event.get('details.LotID', 'N/A')
    try:
        summary['panel_count'] = int(first_start_event.get('details.PanelCount', 0))
    except (ValueError, TypeError):
        summary['panel_count'] = 0
    
    summary['job_start_time'] = first_start_event['timestamp']
    summary['job_status'] = "Started"

    # Find the corresponding completion event after the job started
    df_after_start = df[df['timestamp'] >= summary['job_start_time']]
    end_events = df_after_start[df_after_start['EventName'].isin(['LoadToToolCompleted', 'UnloadFromToolCompleted'])]

    if not end_events.empty:
        first_end_event = end_events.iloc[0]
        summary['job_status'] = "Completed"
        try:
            t_start = datetime.strptime(summary['job_start_time'], "%Y/%m/%d %H:%M:%S.%f")
            t_end = datetime.strptime(first_end_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
            duration = (t_end - t_start).total_seconds()

            if duration >= 0:
                summary['total_duration_sec'] = round(duration, 2)
                if summary['panel_count'] > 0:
                    summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)

            # --- START OF NEW ALARM ANALYSIS LOGIC ---
            job_df = df[(df['timestamp'] >= t_start.strftime("%Y/%m/%d %H:%M:%S.%f")) & 
                        (df['timestamp'] <= t_end.strftime("%Y/%m/%d %H:%M:%S.%f"))]
            
            if 'details.AlarmID' in job_df.columns:
                job_alarms = job_df[job_df['EventName'].isin(['Alarm Set', 'AlarmSet'])]['details.AlarmID'].dropna().unique()
                summary['alarms'] = list(job_alarms)
                summary['unique_alarms_count'] = len(job_alarms)
            # --- END OF NEW ALARM ANALYSIS LOGIC ---

        except (ValueError, TypeError):
            summary['job_status'] = "Time Calculation Error"
    else:
        summary['job_status'] = "Did not complete"
            
    return summary
