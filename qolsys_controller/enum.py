from enum import IntEnum, StrEnum


class QolsysEvent(StrEnum):
    EVENT_PANEL_PARTITION_ADD = "EVENT_PANEL_PARTITION_ADD"
    EVENT_PANEL_ZONE_ADD = "EVENT_PANEL_ZONE_ADD"
    EVENT_PANEL_DOORBELL = "EVENT_PANEL_DOORBELL"
    EVENT_PANEL_CHIME = "EVENT_PANEL_CHIME"
    EVENT_ZWAVE_DEVICE_ADD = "EVENT_ZWAVE_MULTILEVELSENSOR_ADD"
    EVENT_ZWAVE_MULTILEVELSENSOR_ADD = "EVENT_ZWAVE_MULTILEVELSENSOR_ADD"
    EVENT_ZWAVE_METER_ADD = "EVENT_ZWAVE_METER_ADD"
    EVENT_AUTDEV_SENSOR_ADD = "EVENT_AUTDEV_SENSOR_ADD"
    EVENT_AUTDEV_METER_ADD = "EVENT_AUTDEV_METER_ADD"


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
    SMOKE_HEAT = "smoke_heat"
    STAY_INSTANT_MOTION = "stayinstantmotion"
    STAY_DELAY_MOTION = "staydelaymotion"
    AWAY_DELAY_MOTION = "awaydelaymotion"
    EMPTY = ""


class ZoneStatus(StrEnum):
    ACTIVE = "Active"
    ACTIVATED = "Activated"
    ALARMED = "Alarmed"
    ARM_AWAY = "Arm-Away"
    ARM_STAY = "Arm-Stay"
    BELL_TROUBLE = "Bell Trouble"
    CLOSED = "Closed"
    CONNECTED = "connected"
    DISARM = "Disarm"
    FAILURE = "Failure"
    FIRE = "Fire Emergency"
    OPEN = "Open"
    INACTIVE = "Inactive"
    IDLE = "Idle"
    NORMAL = "Normal"
    UNREACHABLE = "Unreachable"
    TAMPERED = "Tampered"
    SYNCHRONIZING = "Synchronizing"
    DISCONNECTED = "disconnected"
    NOT_NETWORKED = "Not Networked"


class DeviceCapability(StrEnum):
    SRF = "SRF"
    WIFI = "WiFi"
    POWERG = "POWERG"
    ZWAVE = "Z-Wave"
    S_LINE = "S-Line"


class AutomationDeviceProtocol(StrEnum):
    ADC = "ADC"
    POWERG = "PowerG"
    ZWAVE = "Z-Wave"
    UNKNOWN = "Unknown"


class ZoneSensorType(StrEnum):
    AUXILIARY_PENDANT = "Auxiliary Pendant"
    BLUETOOTH = "Bluetooth"
    CO_DETECTOR = "CODetector"
    DOORBELL = "Doorbell"
    DOOR_WINDOW = "Door_Window"
    DOOR_WINDOW_M = "Door_Window_M"
    FREEZE = "Freeze"
    GLASS_BREAK = "GlassBreak"
    HEAT = "Heat"
    HIGH_TEMPERATURE = "High Temperature"
    KEY_FOB = "KeyFob"
    KEYPAD = "Keypad"
    MOTION = "Motion"
    OCCUPANCY = "Occupancy Sensor"
    PANEL_GLASS_BREAK = "Panel Glass Break"
    PANEL_MOTION = "Panel Motion"
    SIREN = "Siren"
    SHOCK = "Shock"
    SMOKE_DETECTOR = "SmokeDetector"
    SMOKE_M = "Smoke_M"
    TAKEOVER_MODULE = "TakeoverModule"
    TAMPER = "Tamper Sensor"
    TEMPERATURE = "Temperature"
    TILT = "Tilt"
    TRANSLATOR = "Translator"
    UNKNOWN = "Unknown"
    WATER = "Water"


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
    WATER = "WaterSensor"


class ZWaveNodeStatus(StrEnum):
    NORMAL = "Normal"
    UNREACHABLE = "Unreachable"


class QolsysHvacMode(StrEnum):
    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    HEAT_COOL = "heat_cool"
    FAN_ONLY = "fan_only"
    DRY = "dry"


class QolsysFanMode(StrEnum):
    FAN_ON = "on"
    FAN_OFF = "off"
    FAN_AUTO = "auto"
    FAN_LOW = "low"
    FAN_MEDIUM = "medium"
    FAN_HIGH = "high"
    FAN_CIRCULATE = "Circulate"


class QolsysHvacAction(StrEnum):
    OFF = "off"
    PREHEATING = "preheating"
    HEATING = "heating"
    COOLING = "cooling"
    DRYING = "drying"
    FAN = "fan"
    IDLE = "idle"
    DEFROSTING = "defrosting"


class QolsysTemperatureUnit(StrEnum):
    CELSIUS = "C"
    FAHRENHEIT = "F"


class QolsysSensorScale(StrEnum):
    TEMPERATURE_CELSIUS = "temperature_celsius"
    TEMPERATURE_FAHRENHEIT = "temperature_fahrenheit"
    RELATIVE_HUMIDITY = "relative_humidity"
    WIND_DIRECTION = "wind_direction"
    BAROMETRIC_PRESSURE = "barometric_pressure"
    DEW_POINT = "dew_point"
    RAIN_RATE = "rain_rate"
    TIDE_LEVEL = "tide_level"
    WEIGHT = "weight"
    VOLTS = "volts"
    AMPS = "amps"
    WATTS = "watts"
    DISTANCE = "distance"
    ANGLE_POSITION = "angle_position"
    ROTATION = "rotation"
    WATER_TEMPERATURE_CELSIUS = "water_temperature_celsius"
    WATER_TEMPERATURE_FAHRENHEIT = "water_temperature_fahrenheit"
    LUMINOSITY_LUX = "luminosity_lux"
    UNKNOWN = "unknown"


class QolsysMeterScale(StrEnum):
    UNKNOWN = ""
    KWH = "kWh"
    KVAH = "kVAh"
    WATTS = "W"
    PULSE_COUNT = "pulse"
    VOLTS = "V"
    AMPS = "A"
    POWER_FACTOR = "%"
    KVAR = "kvar"
    KVARH = "kvarh"
    CUBIC_METERS = "m³"
    CUBIC_FEET = "ft³"
    US_GALLONS = "gal"


class QolsysMeterType(IntEnum):
    UNKNOWN = 0x00
    ELECTRIC_METER = 0x01
    GAZ_METER = 0x02
    WATER_METER = 0x03
    HEATING = 0x04
    COOLING = 0x05
    RESERVED = 0x6


class QolsysMeterRateType(IntEnum):
    UNSPECIFIED = 0x00
    IMPORT = 0x01
    EXPORT = 0x02
    RESERVED = 0x03


ZWAVE_QOLSYS_METER_MAP: dict[QolsysMeterType, dict[int, QolsysMeterScale]] = {
    QolsysMeterType.ELECTRIC_METER: {
        0: QolsysMeterScale.KWH,
        1: QolsysMeterScale.KVAH,
        2: QolsysMeterScale.WATTS,
        3: QolsysMeterScale.PULSE_COUNT,
        4: QolsysMeterScale.VOLTS,
        5: QolsysMeterScale.AMPS,
        6: QolsysMeterScale.POWER_FACTOR,
        7: QolsysMeterScale.KVAR,
        8: QolsysMeterScale.KVARH,
    },
    QolsysMeterType.GAZ_METER: {
        0: QolsysMeterScale.CUBIC_METERS,
        1: QolsysMeterScale.CUBIC_FEET,
        3: QolsysMeterScale.PULSE_COUNT,
    },
    QolsysMeterType.WATER_METER: {
        0: QolsysMeterScale.CUBIC_METERS,
        1: QolsysMeterScale.CUBIC_FEET,
        2: QolsysMeterScale.US_GALLONS,
        3: QolsysMeterScale.PULSE_COUNT,
    },
    QolsysMeterType.HEATING: {
        0: QolsysMeterScale.KWH,
        3: QolsysMeterScale.PULSE_COUNT,
    },
    QolsysMeterType.COOLING: {
        0: QolsysMeterScale.KWH,
        3: QolsysMeterScale.PULSE_COUNT,
    },
}

QOLSYS_TO_ZWAVE_METER_MAP: dict[QolsysMeterType, dict[QolsysMeterScale, int]] = {
    QolsysMeterType.ELECTRIC_METER: {
        QolsysMeterScale.KWH: 0,
        QolsysMeterScale.KVAH: 1,
        QolsysMeterScale.WATTS: 2,
        QolsysMeterScale.PULSE_COUNT: 3,
        QolsysMeterScale.VOLTS: 4,
        QolsysMeterScale.AMPS: 5,
        QolsysMeterScale.POWER_FACTOR: 6,
        QolsysMeterScale.KVAR: 7,
        QolsysMeterScale.KVARH: 8,
    },
    QolsysMeterType.GAZ_METER: {
        QolsysMeterScale.CUBIC_METERS: 0,
        QolsysMeterScale.CUBIC_FEET: 1,
        QolsysMeterScale.PULSE_COUNT: 3,
    },
    QolsysMeterType.WATER_METER: {
        QolsysMeterScale.CUBIC_METERS: 0,
        QolsysMeterScale.CUBIC_FEET: 1,
        QolsysMeterScale.US_GALLONS: 2,
        QolsysMeterScale.PULSE_COUNT: 3,
    },
    QolsysMeterType.HEATING: {
        QolsysMeterScale.KWH: 0,
        QolsysMeterScale.PULSE_COUNT: 3,
    },
    QolsysMeterType.COOLING: {
        QolsysMeterScale.KWH: 0,
        QolsysMeterScale.PULSE_COUNT: 3,
    },
}


def map_to_qolsys_meter_scale(
    zwave_meter_type: QolsysMeterType,
    zwave_meter_scale: int,
) -> QolsysMeterScale:
    dict_scale = ZWAVE_QOLSYS_METER_MAP.get(zwave_meter_type, None)
    if dict_scale is not None:
        return dict_scale.get(zwave_meter_scale, QolsysMeterScale.UNKNOWN)
    return QolsysMeterScale.UNKNOWN


def map_to_zwave_meter_scale(
    meter_type: QolsysMeterType,
    meter_scale: QolsysMeterScale,
) -> int:
    dict_scale = QOLSYS_TO_ZWAVE_METER_MAP.get(meter_type, None)
    if dict_scale is not None:
        return dict_scale.get(meter_scale, 0)
    return 0
