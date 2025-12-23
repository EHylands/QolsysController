from enum import Enum, IntEnum


class vdFuncType(IntEnum):
    BINARY_ACTUATOR = 1
    MULTISTATE_ACTUATOR = 2
    LEVEL = 3
    STATUS = 4
    MOMENTARY_ACTION = 5
    MODE_SELECTOR = 6
    EVENT = 7


class vdFuncName(Enum):
    OPEN_CLOSE = "Open/Close"
    LOCK_UNLOCK = "Lock/Unlock"
    ON_OFF = "On/Off"


class vdFuncLocalControl(IntEnum):
    NONE = 0
    STATUS_ONLY = 1
    FULL_CONTROL = 2


class vdFuncState(IntEnum):
    ON = 0
    OFF = 1
