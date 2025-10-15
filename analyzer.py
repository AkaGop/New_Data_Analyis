# analyzer.py
from datetime import datetime
import pandas as pd
from config import ALARM_CODE_MAP

def perform_eda(df: pd.DataFrame) -> dict:
    eda_results = {}
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')
    if 'details.AlarmID' in df.columns:
        alarm_events = df[df['details.AlarmID'].notna()].copy()
        if not alarm_events.empty:
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            alarm_events['AlarmText'] = alarm_ids.map(ALARM_CODE_MAP).fillna("Unknown Alarm ID")
            eda_results['alarm_counts'] = alarm_events['AlarmText'].value_counts()
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID', 'AlarmText']]
        else:
            eda_results['alarm_counts'] = pd.Series(dtype='int64')
            eda_results['alarm_table'] = pd.DataFrame()
    else:
        eda_results['alarm_counts'] = pd.Series(dtype='int64')
        eda_results['alarm_table'] = pd.DataFrame()
    return eda_results

def analyze_data(events: list) -> dict:
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "job_start_time": "N/A", "job_end_time": "N/A", "total_duration_sec": 0.0,
        "avg_cycle_time_sec": 0.0, "job_status": "No Job Found", "control_state_changes": []
    }
    if not events: return summary
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    if start_event:
        lot_id = start_event['details'].get('LotID', 'N/A')
        if lot_id == 'N/A' or not lot_id:
            found_lot_id = next((e['details'].get('LotID') for e in events if e.get('details', {}).get('LotID')), 'N/A')
            summary['lot_id'] = found_lot_id
        else:
            summary['lot_id'] = lot_id
        try:
            summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except (ValueError, TypeError): summary['panel_count'] = 0
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
            except (ValueError, TypeError): summary['job_status'] = "Time Calculation Error"
    else:
        panel_activity = any(e.get('details', {}).get('CEID') in [120, 127] for e in events)
        if panel_activity: summary['lot_id'] = "Dummy/Test Panels"
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
        ceid = details.get('CEID')
        if ceid == 12: summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "LOCAL"})
        elif ceid == 13: summary['control_state_changes'].append({"Timestamp": event['timestamp'], "State": "REMOTE"})
    return summary
