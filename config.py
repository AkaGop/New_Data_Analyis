# config.py
"""
Single source of truth for all static configuration data.
This map is now greatly expanded based on the Hirata documentation.
"""
CEID_MAP = {
    # GEM Events
    7: "GemOpCommand",
    11: "Equipment Offline",
    12: "Control State Local",
    13: "Control State Remote",
    14: "GemMsgRecognition",
    16: "PP-SELECT Changed",
    30: "Process State Change",
    101: "Alarm Cleared",
    102: "Alarm Set",

    # EPT Events
    51: "EPTStateChange0",

    # Equipment Inherent Events (from PDF pages 92-94)
    120: "IDRead",
    121: "UnloadedFromMag",
    122: "LoadedToMag",
    126: "UnloadedFromTool",
    127: "LoadedToTool",
    128: "PP-Selected",
    131: "LoadToToolCompleted",
    132: "UnloadFromToolCompleted",
    133: "MagToMagCompleted",
    134: "MagCheckedCompleted",
    136: "MappingCompleted",
    141: "PortStatusChange",
    142: "IDReaderStateChanged",
    143: "DriveStateChange",
    144: "ModeSetCompleted",
    145: "ReplyIDReadModeChanged",
    151: "LoadStarted",
    152: "UnloadStarted",
    153: "MagToMagStarted",
    154: "MagCheckStarted",
    156: "CheckSlotStarted",
    161: "PortCMDCanceled",
    180: "RequestMagazineDock",
    181: "MagazineDocked",
    182: "MagazineUndocked",
    183: "RequestOperatorIdCheck",
    184: "RequestOperatorLogin",
    185: "RequestMappingCheck",
    187: "ESDRead",
    188: "DEFRead",
    192: "BufferCapacityChanged",
    193: "BufferModeChanged",
    194: "LoadedToBufferShuttle1",
    195: "LoadedToBufferShuttle2",
    196: "UnloadedFromToolShuttle1",
    197: "UnloadedFromBufferShuttle2",
    198: "MappingCompletedShuttle1",
    199: "MappingCompletedShuttle2",
    
    # Custom/Alarm related CEIDs found in logs
    18: "AlarmSet",
    113: "AlarmSet",
    114: "AlarmSet",
}

RPTID_MAP = {
    # GEM Reports
    8: ['OperatorCommand'],
    11: ['ControlState'],
    14: ['Clock'],
    16: ['PPChangeName', 'PPChangeStatus'],
    32: ['ProcessState', 'PreviousProcessState'],
    101:['AlarmID', 'AlarmSet'],

    # EPT Reports
    51: ['EqpName', 'EPTState', 'PreviousEPTState', 'EPTStateTime', 'TaskName', 'TaskType', 'PreviousTaskName', 'PreviousTaskType', 'BlockedReason', 'BlockedReasonText'],

    # Equipment Inherent Reports (from PDF pages 95-96)
    108: ['PPID'],
    120: ['LotID', 'PanelID', 'Orientation', 'ResultCode', 'SlotID'],
    121: ['LotID', 'PanelID', 'SourcePortID'],
    122: ['LotID'],
    123: ['PortID', 'SlotList'],
    124: ['LotID', 'SourcePortID', 'DestPortID'],
    125: ['LotID', 'PanelID', 'SlotID', 'DestPortID'],
    141: ['PortID', 'PortStatus'],
    142: ['IDReaderState'],
    143: ['EquipmentID', 'DriveState'],
    144: ['LPMode'],
    145: ['ReplyIDReadMode'],
    150: ['MagazineID'],
    151: ['PortID', 'MagazineID', 'OperatorID'],
    152: ['OperatorID'],
}
