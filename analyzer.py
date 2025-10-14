# analyzer.py
from datetime import datetime

def analyze_data(events: list) -> dict:
    summary = {
        "control_state": "Unknown", "lot_id": "N/A", "panel_count": 0,
        "total_duration_sec": 0.0, "avg_cycle_time_sec": 0.0,
    }
    # Find the last known control state
    for event in reversed(events):
        if event.get('details', {}).get('ControlState'):
            state_val = event['details']['ControlState']
            if state_val == '4': summary['control_state'] = 'Online Local'
            elif state_val == '5': summary['control_state'] = 'Remote'
            break
    
    start_event = next((e for e in events if e.get('details', {}).get('RCMD') in ['LOADSTART', 'UNLOADSTART']), None)
    if start_event:
        lot_id = start_event['details'].get('LotID', '').strip()
        summary['lot_id'] = lot_id if lot_id else "Test / Dummy Lot"
        summary['panel_count'] = int(start_event['details'].get('PanelCount', 0))
        
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
            except (ValueError, TypeError): pass
    return summary
