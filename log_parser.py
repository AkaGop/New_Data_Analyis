# log_parser.py

import re
from io import StringIO
from config import CEID_MAP, RPTID_MAP

def _find_enclosed_list(text):
    """
    A robust helper function to find the content of the first top-level <L[...]...> block.
    It correctly handles nested brackets.
    """
    # Find the start of the first list declaration
    match = re.search(r"<\s*L\s*\[\d+\]\s*", text)
    if not match:
        return ""
    
    body_start = match.end()
    balance = 1
    for i in range(body_start, len(text)):
        if text[i] == '<':
            balance += 1
        elif text[i] == '>':
            balance -= 1
        
        if balance == 0:
            # We found the matching closing bracket for the initial list.
            return text[body_start:i]
            
    return "" # Should not happen in well-formed data

def _get_primitive_tokens(text_block):
    """Extracts all primitive <A...> and <U...> values from a given block of text."""
    if not text_block: return []
    # This regex finds all A or U tags and captures their value, whether it's quoted or numeric.
    tokens = re.findall(r"<(?:A|U\d)\s\[\d+\]\s(?:'([^']*)'|(\d+))>", text_block)
    # The regex produces tuples of ('value', '') for strings or ('', 'value') for numbers.
    # This list comprehension flattens it into a single clean list.
    return [s if s else i for s, i in tokens]

def _parse_s6f11_report(full_text: str) -> dict:
    """
    Final, robust, and structurally-aware parser for S6F11 reports.
    """
    data = {}
    
    # Isolate the main <L,3> body of the S6F11 message.
    s6f11_body = _find_enclosed_list(full_text)
    if not s6f11_body: return {}

    # Extract all top-level items from the main body.
    top_level_tokens = _get_primitive_tokens(s6f11_body)
    
    # We expect at least two tokens (DATAID, CEID) before the report list.
    if len(top_level_tokens) < 2: return {}
    
    try:
        ceid = int(top_level_tokens[1])
        
        # Isolate the text for the list of reports, which comes after the CEID tag.
        ceid_tag_match = re.search(r'<\s*U\d\s*\[\d+\]\s*' + str(ceid) + r'\s*>', s6f11_body)
        if not ceid_tag_match: return {}
        report_list_text = s6f11_body[ceid_tag_match.end():]
        
    except (ValueError, IndexError):
        return {}

    # The report itself is the first list inside the report_list_text
    report_body = _find_enclosed_list(report_list_text)
    if not report_body: return {}

    report_tokens = _get_primitive_tokens(report_body)
    if not report_tokens: return {}
    
    try:
        rptid = int(report_tokens[0])
    except (ValueError, IndexError):
        return {}

    # Populate the final data dictionary
    if ceid in CEID_MAP:
        data['CEID'] = ceid
        if "Alarm" in CEID_MAP.get(ceid, ''): data['AlarmID'] = ceid
    
    if rptid in RPTID_MAP:
        data['RPTID'] = rptid
        data_payload = report_tokens[1:]
        field_names = RPTID_MAP.get(rptid, [])
        for i, name in enumerate(field_names):
            if i < len(data_payload):
                data[name] = data_payload[i]
            
    return data

def _parse_s2f49_command(full_text: str) -> dict:
    data = {}
    rcmd_match = re.search(r"<\s*A\s*\[\d+\]\s*'([A-Z_]{5,})'", full_text)
    if rcmd_match: data['RCMD'] = rcmd_match.group(1)
    lotid_match = re.search(r"'LOTID'\s*>\s*<A\[\d+\]\s*'([^']*)'", full_text, re.IGNORECASE)
    if lotid_match: data['LotID'] = lotid_match.group(1)
    panels_match = re.search(r"'LOTPANELS'\s*>\s*<L\s\[(\d+)\]", full_text, re.IGNORECASE)
    if panels_match: data['PanelCount'] = int(panels_match.group(1))
    return data

def parse_log_file(uploaded_file):
    events = []
    if not uploaded_file: return events
    try: lines = StringIO(uploaded_file.getvalue().decode("utf-8")).readlines()
    except: lines = StringIO(uploaded_file.getvalue().decode("latin-1", errors='ignore')).readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i+= 1; continue
        
        header_match = re.match(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+),\[([^\]]+)\],(.*)", line)
        if not header_match: i += 1; continue
        
        timestamp, log_type, message_part = header_match.groups()
        
        msg_match = re.search(r"MessageName=(\w+)|Message=.*?:\'(\w+)\'", message_part)
        msg_name = (msg_match.group(1) or msg_match.group(2)) if msg_match else "N/A"
        
        event = {"timestamp": timestamp, "log_type": log_type, "msg_name": msg_name}
        
        if ("Core:Send" in log_type or "Core:Receive" in log_type) and i + 1 < len(lines) and lines[i+1].strip().startswith('<'):
            j = i + 1
            block_lines = []
            while j < len(lines) and lines[j].strip() != '.':
                block_lines.append(lines[j]); j += 1
            i = j
            
            if block_lines:
                full_text = "".join(block_lines)
                details = {}
                if msg_name == 'S6F11': details = _parse_s6f11_report(full_text)
                elif msg_name == 'S2F49': details = _parse_s2f49_command(full_text)
                if details: event['details'] = details
        
        # We only want to see events that we successfully parsed details for.
        if 'details' in event:
            events.append(event)
        i += 1
            
    return events
