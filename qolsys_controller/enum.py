from enum import StrEnum


class PartitionSystemStatus(StrEnum):
    ARM_STAY = "ARM-STAY"
    ARM_AWAY = "ARM-AWAY"
    ARM_NIGHT = "ARM-NIGHT"
    DISARM = "DISARM"
    ARM_AWAY_EXIT_DELAY = "ARM-AWAY-EXIT-DELAY"
    ARM_STAY_EXIT_DELAY = "ARM-STAY-EXIT-DELAY"
    ARM_NIGHT_EXIT_DELAY = "ARM-NIGHT-EXIT-DELAY"
    UNKNOWN = "UNKNOWN"


class PartitionArmingType(StrEnum):
    ARM_STAY = "ui_armstay"
    ARM_AWAY = "ui_armaway"
    ARM_NIGHT = "ui_armnight"


class PartitionAlarmState(StrEnum):
    NONE = "None"
    DELAY = "Delay"
    ALARM = "Alarm"
    UNKNOWN = "UNKNOWN"


class PartitionAlarmType(StrEnum):
    POLICE_EMERGENCY = "Police Emergency"
    FIRE_EMERGENCY = "Fire Emergency"
    AUXILIARY_EMERGENCY = "Auxiliary Emergency"
    SILENT_AUXILIARY_EMERGENCY = "Silent Auxiliary Emergency"
    SILENT_POLICE_EMERGENCY = "Silent Police Emergency"
    GLASS_BREAK_AWAY_ONLY = "glassbreakawayonly"
    GLASS_BREAK = "glassbreak"
    ENTRY_EXIT_NORMAL_DELAY = "entryexitdelay"
    ENTRY_EXIT_LONG_DELAY = "entryexitlongdelay"
    INSTANT_PERIMETER_DW = "instantperimeter"
    INSTANT_INTERIOR_DOOR = "instantinterior"
    AWAY_INSTANT_FOLLOWER_DELAY = "awayinstantfollowerdelay"
    REPORTING_SAFETY_SENSOR = "reportingsafety"
    DELAYED_REPORTING_SAFETY_SENSOR = "delayedreportingsafety"
    AWAY_INSTANT_MOTION = "awayinstantmotion"
    STAY_INSTANT_MOTION = "stayinstantmotion"
    STAY_DELAY_MOTION = "staydelaymotion"
    AWAY_DELAY_MOTION = "awaydelaymotion"
    EMPTY = ""


class ZoneStatus(StrEnum):
    ALARMED = "Alarmed"
    OPEN = "Open"
    CLOSED = "Closed"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ACTIVATED = "Activated"
    IDLE = "Idle"
    NORMAL = "Normal"
    UNREACHABLE = "Unreachable"
    TAMPERED = "Tampered"
    SYNCHONIZING = "Synchonizing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILURE = "Failure"
    NOT_NETWORKED = "Not Networked"
    DISARM = "Disarm"


class DeviceCapability(StrEnum):
    SRF = "SRF"
    WIFI = "WiFi"
    POWERG = "POWERG"
    ZWAVE = "Z-Wave"


class ZoneSensorType(StrEnum):
    DOOR_WINDOW = "Door_Window"
    DOORBELL = "Doorbell"
    MOTION = "Motion"
    GLASS_BREAK = "GlassBreak"
    KEY_FOB = "KeyFob"
    KEYPAD = "Keypad"
    AUXILIARY_PENDANT = "Auxiliary Pendant"
    SMOKE_DETECTOR = "SmokeDetector"
    CO_DETECTOR = "CODetector"
    # HARDWIRE_TRANSLATOR = "" # TBD
    # WIRELESS_TRANSLATOR = "" #TBD
    TEMPERATURE = "Temperature"
    HEAT = "Heat"
    WATER = "Water"
    SHOCK = "Shock"
    FREEZE = "Freeze"
    TILT = "Tilt"
    SMOKE_M = "Smoke_M"
    # DOOR_WINDOW_M = "" #TBD
    # OCCUPANCY = ""  #TBD
    SIREN = "Siren"
    # HIGH_TEMPERATURE = "" # TBD
    PANEL_MOTION = "Panel Motion"
    PANEL_GLASS_BREAK = "Panel Glass Break"
    BLUETOOTH = "Bluetooth"
    TAKEOVER_MODULE = "TakeoverModule"
    TRANSLATOR = "Translator"
    TAMPER = "Tamper Sensor"


class ZoneSensorGroup(StrEnum):
    CO = "co"
    FIXED_INTRUSION = "fixedintrusion"
    FIXED_SILENT = "fixedsilentkey"
    MOBILE_INTRUSION = "mobileintrusion"
    MOBILE_SILENT = "mobilesilentkey"
    FIXED_AUXILIARY = "fixedmedical"
    FIXED_SILENT_AUXILIARY = "fixedsilentmedical"
    LOCAL_SAFETY_SENSOR = "localsafety"
    MOBILE_AUXILIARY = "mobilemedical"
    MOBILE_SILENT_AUXILIARY = "mobilesilentmedical"
    SAFETY_MOTION = "safetymotion"
    GLASS_BREAK = "glassbreak"
    GLASS_BREAK_AWAY_ONLY = "glassbreakawayonly"
    SMOKE_HEAT = "smoke_heat"
    TAMPER_ZONE = "tamperzone"
    SHOCK = "shock"
    ENTRY_EXIT_NORMAL_DELAY = "entryexitdelay"
    ENTRY_EXIT_LONG_DELAY = "entryexitlongdelay"
    INSTANT_PERIMETER_DW = "instantperimeter"
    INSTANT_INTERIOR_DOOR = "instantinterior"
    AWAY_INSTANT_FOLLOWER_DELAY = "awayinstantfollowerdelay"
    REPORTING_SAFETY_SENSOR = "reportingsafety"
    DELAYED_REPORTING_SAFETY_SENSOR = "delayedreportingsafety"
    AWAY_INSTANT_MOTION = "awayinstantmotion"
    STAY_INSTANT_MOTION = "stayinstantmotion"
    STAY_DELAY_MOTION = "staydelaymotion"
    AWAY_DELAY_MOTION = "awaydelaymotion"

    # TAKEOVER = "" #TBD
    # GARAGE_TILT_SAFETY = "" # TBD
    # WATER_SENSOR = "" # TBD
    # WATER_SENSOR_NON_REPORTING = "" # TBD
    # SHOCK_GLASS_BREAK = "" # TBD
    # SHOCK_GLASS_BREAK_AWAY_ONLY = "" # TBD
    # FREEZE = "" # TBD
    # FREEZE_NON_REPORTING = "" # TBD
    # TEMP_REPORTING = "" #TBD
    # TEMP_NON_REPORTING = "" #TBD
    # SIREN = "" # TBD


class ZWaveNodeStatus(StrEnum):
    NORMAL = "Normal"
    UNREACHABLE = "Unreachable"
