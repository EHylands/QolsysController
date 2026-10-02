from enum import Enum, IntEnum

from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode


class vdFuncType(IntEnum):
    BINARY_ACTUATOR = 1
    LIGHT = 3
    TEMPERATURE = 4
    MALFUNCTION = 10
    DIMMER = 12
    HUMIDITY = 20
    HEAT_SETPOINT = 21
    MIN_HEAT_SETPOINT = 22
    MAX_HEAT_SETPOINT = 23
    COOL_SETPOINT = 24
    MIN_COOL_SETPOINT = 25
    MAX_COOL_SETPOINT = 26
    THERMOSTAT_MODE = 27
    FAN_MODE = 28
    TEMPERATURE_UNITS = 29
    SUPPORTED_THERMOSTAT_MODES = 30
    UNKNOWN = 99


class vdFuncName(Enum):
    OPEN_CLOSE = "Open/Close"
    LOCK_UNLOCK = "Lock/Unlock"
    OFF_ON = "Off/On"
    MALFUNCTION = "Malfunction"
    HEAT_SETPOINT = "Heat Setpoint"
    MIN_HEAT_SETPOINT_LIMIT = "Min Heat Setpoint Limit"
    MAX_HEAT_SETPOINT_LIMIT = "Max Heat Setpoint Limit"
    COOL_SETPOINT = "Cool Setpoint"
    MIN_COOL_SETPOINT_LIMIT = "Min Cool Setpoint Limit"
    MAX_COOL_SETPOINT_LIMIT = "Max Cool Setpoint Limit"
    THERMOSTAT_SYSTEM_MODE = "Thermostat System Mode"
    FAN_MODE = "Fan Mode"
    TEMPERATURE_UNITS = "Temperature Units"
    THERMOSTAT_SYSTEM_MODES_SUPPORTED = "Thermostat System Modes Supported"
    LOCAL_TEMPERATURE = "Local Temperature"
    HUMIDITY_IN_PERCENTAGE = "Humidity In Percentage"


class vdFuncLocalControl(IntEnum):
    NONE = 0
    STATUS_ONLY = 1
    FULL_CONTROL = 2


class vdFuncState(IntEnum):
    OFF = 0
    ON = 1


class AdcThermostatMode(IntEnum):
    OFF = 0
    HEAT_COOL = 1
    COOL = 2
    HEAT = 3


class AdcFanMode(IntEnum):
    ON = 0
    AUTO = 5


ADC_TO_QOLSYS_THERMOSTAT_MODE: dict[AdcThermostatMode, QolsysHvacMode] = {
    AdcThermostatMode.OFF: QolsysHvacMode.OFF,
    AdcThermostatMode.HEAT_COOL: QolsysHvacMode.HEAT_COOL,
    AdcThermostatMode.COOL: QolsysHvacMode.COOL,
    AdcThermostatMode.HEAT: QolsysHvacMode.HEAT,
}

QOLSYS_TO_ADC_THERMOSTAT_MODE: dict[QolsysHvacMode, AdcThermostatMode] = {
    QolsysHvacMode.OFF: AdcThermostatMode.OFF,
    QolsysHvacMode.HEAT_COOL: AdcThermostatMode.HEAT_COOL,
    QolsysHvacMode.COOL: AdcThermostatMode.COOL,
    QolsysHvacMode.HEAT: AdcThermostatMode.HEAT,
}

ADC_TO_QOLSYS_FAN_MODE: dict[AdcFanMode, QolsysFanMode] = {
    AdcFanMode.ON: QolsysFanMode.FAN_ON,
    AdcFanMode.AUTO: QolsysFanMode.FAN_AUTO,
}

QOLSYS_TO_ADC_FAN_MODE: dict[QolsysFanMode, AdcFanMode] = {
    QolsysFanMode.FAN_ON: AdcFanMode.ON,
    QolsysFanMode.FAN_AUTO: AdcFanMode.AUTO,
}
