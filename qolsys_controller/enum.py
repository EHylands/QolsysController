from enum import StrEnum


class PartitionSystemStatus(StrEnum):
    ARM_STAY = "ARM-STAY"
    ARM_AWAY = "ARM-AWAY"
    DISARM = "DISARM"
    ARM_AWAY_EXIT_DELAY = "ARM-AWAY-EXIT-DELAY"
    ARM_STAY_EXIT_DELAY = "ARM-STAY-EXIT-DELAY"

class PartitionAlarmState(StrEnum):
        NONE = "None"
        DELAY = "Delay"
        ALARM = "Alarm"

class PartitionAlarmType(StrEnum):
    POLICE_EMERGENCY = "Police Emergency"
    FIRE_EMERGENCY = "Fire Emergency"
    AUXILIARY_EMERGENCY = "Auxiliary Emergency"
    SILENT_AUXILIARY_EMERGENCY = "Silent Auxiliary Emergency"
    SILENT_POLICE_EMERGENCY = "Silent Police Emergency"

class ZoneStatus(StrEnum):
    OPEN = "Open"
    CLOSED = "Closed"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ACTIVATED = "Activated"
    IDLE = "Idle"
    UNREACHABLE = "Unreachable"
    TAMPERED = "Tampered"
    SYNCHONIZING = "Synchonizing"
    CONNECTED = "connected"

class ZoneSensorType(StrEnum):
    DOOR_WINDOW = "Door_Window"
    MOTION = "Motion"
    PANEL_MOTION = "Panel Motion"
    GLASS_BREAK = "GlassBreak"
    PANEL_GLASS_BREAK = "Panel Glass Break"
    BLUETOOTH = "Bluetooth"
    SMOKE_DETECTOR = "SmokeDetector"
    CO_DETECTOR = "CODetector"
    WATER = "Water"
    FREEZE = "Freeze"
    HEAT = "Heat"
    TILT = "Tilt"
    KEYPAD = "Keypad"
    AUXILIARY_PENDANT = "Auxiliary Pendant"
    SIREN = "Siren"
    KEY_FOB = "KeyFob"
    TEMPERATURE = "Temperature"
    TAKEOVER_MODULE = "TakeoverModule"
    TRANSLATOR = "Translator"
    DOORBELL = "Doorbell"
    SHOCK = "Shock"


