from enum import Enum, IntEnum


class MeterType(IntEnum):
    UNKNOWN = 0x00
    ELECTRIC_METER = 0x01
    GAZ_METER = 0x02
    WATER_METER = 0x03
    HEATING = 0x04
    COOLING = 0x05
    RESERVED = 0x6


class MeterRateType(IntEnum):
    UNSPECIFIED = 0x00
    IMPORT = 0x01
    EXPORT = 0x02
    RESERVED = 0x03


class ZWaveUnknownMeterScale(IntEnum):
    UNKNOWN = 0


class ZWaveElectricMeterScale(IntEnum):
    KWH = 0
    KVAH = 1
    WATTS = 2
    PULSE_COUNT = 3
    VOLTS = 4
    AMPS = 5
    POWER_FACTOR = 6
    KVAR = 7
    KVARH = 8


class ZWaveGasMeterScale(IntEnum):
    CUBIC_METERS = 0  # m³
    CUBIC_FEET = 1  # ft³
    PULSE_COUNT = 3


class ZWaveWaterMeterScale(IntEnum):
    CUBIC_METERS = 0  # m³
    CUBIC_FEET = 1  # ft³
    US_GALLONS = 2
    PULSE_COUNT = 3


class ZWaveThermalMeterScale(IntEnum):
    KWH = 0
    PULSE_COUNT = 3


class ThermostatMode(IntEnum):
    OFF = 0x00
    HEAT = 0x01
    COOL = 0x02
    AUTO = 0x03
    AUX_HEAT = 0x04
    RESUME = 0x05
    FAN_ONLY = 0x06
    FURNACE = 0x07
    DRY_AIR = 0x08
    MOIST_AIR = 0x09
    AUTO_CHANGEOVER = 0x0A
    ENERGY_SAVE_HEAT = 0x0B
    ENERGY_SAVE_COOL = 0x0C
    AWAY = 0x0F


BITMASK_SUPPORTED_THERMOSTAT_MODE = {
    0: ThermostatMode.OFF,
    1: ThermostatMode.HEAT,
    2: ThermostatMode.COOL,
    3: ThermostatMode.AUTO,
    4: ThermostatMode.AUX_HEAT,
    5: ThermostatMode.RESUME,
    6: ThermostatMode.FAN_ONLY,
    7: ThermostatMode.FURNACE,
}


class ThermostatFanMode(IntEnum):
    AUTO_LOW = 0x00
    LOW = 0x01
    AUTO_HIGH = 0x02
    HIGH = 0x03
    AUTO_MEDIUM = 0x04
    MEDIUM = 0x05
    CIRCULATION = 0x06
    HUMIDITY_CIRCULATION = 0x07
    LEFT_RIGHT = 0x08
    UP_DOWN = 0x09
    QUIET = 0x0A
    EXTERNAL_CIRCULATION = 0x0800


BITMASK_SUPPORTED_THERMOSTAT_FAN_MODE = {
    0: ThermostatFanMode.AUTO_LOW,
    1: ThermostatFanMode.LOW,
    2: ThermostatFanMode.AUTO_HIGH,
    3: ThermostatFanMode.HIGH,
    4: ThermostatFanMode.AUTO_MEDIUM,
    5: ThermostatFanMode.MEDIUM,
    6: ThermostatFanMode.CIRCULATION,
    7: ThermostatFanMode.HUMIDITY_CIRCULATION,
}


class ThermostatSetPointMode(IntEnum):
    HEATING_1 = 0x00
    COOLING_1 = 0x01
    HEATING_2 = 0x02
    COOLING_2 = 0x03
    AWAY_HEATING_1 = 0x04
    AWAY_COOLING_1 = 0x05


BITMASK_SUPPORTED_THERMOSTAT_SETPOINT = {
    0: ThermostatSetPointMode.HEATING_1,
    1: ThermostatSetPointMode.COOLING_1,
    2: ThermostatSetPointMode.HEATING_2,
    3: ThermostatSetPointMode.COOLING_2,
    4: ThermostatSetPointMode.AWAY_HEATING_1,
    5: ThermostatSetPointMode.AWAY_COOLING_1,
}


class ZwaveCommandClass(IntEnum):
    SwitchBinary = 0x25
    SwitchMultilevel = 0x26
    SensorMultiLevel = 0x31
    Meter = 0x32
    ThermostatMode = 0x40
    ThermostatSetPoint = 0x43
    ThermostatFanMode = 0x44
    ThermostatFanState = 0x45
    DoorLock = 0x62
    Alarm = 0x71


class ZwaveCommand(IntEnum):
    SET = 0x01
    GET = 0x02


class ZwaveDeviceClass(Enum):
    Unknown = 0x00
    GenericController = 0x01
    StaticController = 0x02
    AVControlPoint = 0x03
    Display = 0x04
    DoorLock = 0x05
    Thermostat = 0x06
    SensorBinary = 0x07
    SensorMultilevel = 0x08
    Meter = 0x09
    EntryControl = 0x0A
    SemiInteroperable = 0x0B
    Button = 0x0C
    RepeaterSlave = 0x0F
    SwitchBinary = 0x10
    SwitchMultilevel = 0x11
    RemoteSwitchBinary = 0x12
    RemoteSwitchMultilevel = 0x13
    SwitchToggleBinary = 0x14
    SwitchToggleMultilevel = 0x15
    ZIPNode = 0x16
    Ventilation = 0x17
    WindowCovering = 0x18
    BarrierOperator = 0x20
    SensorNotification = 0x21
    SoundSwitch = 0x22
    MeterPulse = 0x23
    ColorSwitch = 0x24
    ClimateControlSchedule = 0x25
    RemoteAssociationActivator = 0x26
    SceneController = 0x27
    SceneSceneActuatorConfiguration = 0x28
    SimpleAVControlPoint = 0x30
