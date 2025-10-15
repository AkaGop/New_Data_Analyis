from datetime import datetime
import pandas as pd

def perform_eda(df: pd.DataFrame) -> dict:
    eda_results = {}
    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else: eda_results['event_counts'] = pd.Series(dtype='int64')
    if 'details.AlarmID' in df.columns:
        alarm_events = df[df['details.AlarmID'].notna()].copy()
        if not alarm_events.empty:
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            eda_results['alarm_counts'] = alarm_ids.value_counts()
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID']]
        else:
            eda_results['alarm_counts'] = pd.Series(dtype='int64'); eda_results['alarm_table'] = pd.DataFrame()
    else:
        eda_results['alarm_counts'] = pd.Series(dtype='int64'); eda_results['alarm_table'] = pd.DataFrame()
    return eda_results

def analyze_data(events: list) -> dict:
    summary = {
        "operators": set(), "magazines": set(), "lot_id": "N/A", "panel_count": 0,
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
    }
    if not events: return summary
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') == 'LOADSTART'), None)
    if start_event:
        summary['lot_id'] = start_event['details'].get('LotID', 'N/A')
        try: summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        except: summary['panel_count'] = 0
        start_index = events.index(start_event)
        end_event = next((e for e in events[start_index:] if e.get('details', {}).get('CEID') in [131, 132]), None)
        if end_event:
            try:
                t_start = datetime.strptime(start_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                t_end = datetime.strptime(end_event['timestamp'], "%Y/%m/%d %H:%M:%S.%f")
                duration = (t_end - t_start).total_seconds()
                if duration >= 0:
                    summary['total_duration_sec'] = round(duration, 2)
                    if summary['panel_count'] > 0:
                        summary['avg_cycle_time_sec'] = round(duration / summary['panel_count'], 2)
            except: pass
    if summary['lot_id'] == 'N/A':
        summary['lot_id'] = "Test Lot / No Job"
    for event in events:
        details = event.get('details', {})
        if details.get('OperatorID'): summary['operators'].add(details['OperatorID'])
        if details.get('MagazineID'): summary['magazines'].add(details['MagazineID'])
    return summary
