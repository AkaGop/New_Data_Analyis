# analyzer.py
from datetime import datetime
import pandas as pd
# Import the new map
from config import ALARM_CODE_MAP

def perform_eda(df: pd.DataFrame) -> dict:
    """
    A robust EDA function that defensively checks for column existence
    and now includes alarm description lookups.
    """
    eda_results = {}

    if 'EventName' in df.columns:
        eda_results['event_counts'] = df['EventName'].value_counts()
    else:
        eda_results['event_counts'] = pd.Series(dtype='int64')

    # --- START OF HIGHLIGHTED CHANGE ---
    # The Alarm Analysis section is now enhanced.
    if 'details.AlarmID' in df.columns:
        # Create a copy to safely add new columns
        alarm_events = df[df['details.AlarmID'].notna()].copy()
        
        if not alarm_events.empty:
            alarm_ids = pd.to_numeric(alarm_events['details.AlarmID'], errors='coerce').dropna()
            
            # Create a new column for the alarm description by mapping the ID
            alarm_events['AlarmText'] = alarm_ids.map(ALARM_CODE_MAP).fillna("Unknown Alarm ID")
            
            # The bar chart will now be based on the readable text
            eda_results['alarm_counts'] = alarm_events['AlarmText'].value_counts()
            
            # The table will include the timestamp, ID, and the new description
            eda_results['alarm_table'] = alarm_events[['timestamp', 'EventName', 'details.AlarmID', 'AlarmText']]
        else:
            # If there are no valid alarm events, create empty results
            eda_results['alarm_counts'] = pd.Series(dtype='int64')
            eda_results['alarm_table'] = pd.DataFrame()
    else:
        # If the AlarmID column doesn't even exist, create empty results
        eda_results['alarm_counts'] = pd.Series(dtype='int64')
        eda_results['alarm_table'] = pd.DataFrame()
    # --- END OF HIGHLIGHTED CHANGE ---
        
    return eda_results

# The analyze_data function is correct and does not need any changes.
def analyze_data(events: list) -> dict:
    # ... (code remains the same as previous step) 
