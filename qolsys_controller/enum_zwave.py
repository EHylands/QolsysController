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
    OFF = 0x0001
    HEAT = 0x0002
    COOL = 0x0004
    AUTO = 0x0008
    AUX_HEAT = 0x0010
    RESUME = 0x0020
    FAN_ONLY = 0x0040
    FURNACE = 0x0080
    DRY_AIR = 0x0100
    MOIST_AIR = 0x0200
    AUTO_CHANGEOVER = 0x0400
    ENERGY_SAVE_HEAT = 0x0800
    ENERGY_SAVE_COOL = 0x1000
    AWAY = 0x2000
    FULL_POWER = 0x4000
    MANUFACTURER_SPECEFIC = 0x8000


class ThermostatFanMode(IntEnum):
    AUTO_LOW = 0x0001
    LOW = 0x0002
    AUTO_HIGH = 0x0004
    HIGH = 0x0008
    AUTO_MEDIUM = 0x0010
    MEDIUM = 0x0020
    CIRCULATION = 0x4000
    HUMIDITY_CIRCULATION = 0x0080
    LEFT_RIGHT = 0x0100
    UP_DOWN = 0x0200
    QUIET = 0x0400
    EXTERNAL_CIRCULATION = 0x0800
    MANUFACTURER_SPECEFIC = 0x1000


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
