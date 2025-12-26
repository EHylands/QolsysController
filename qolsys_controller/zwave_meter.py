__all__ = ["QolsysMeterDevice", "QolsysMeterSensor"]

import logging
from enum import IntEnum

from qolsys_controller.enum_zwave import (
    MeterRateType,
    MeterType,
    ZwaveCommand,
    ZwaveCommandClass,
    ZWaveElectricMeterScale,
    ZWaveGasMeterScale,
    ZWaveThermalMeterScale,
    ZWaveUnknownMeterScale,
    ZWaveWaterMeterScale,
)

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysMeterSensor:
    def __init__(
        self,
        parent_device: "QolsysMeterDevice",
        meter_type: MeterType,
        rate_type: MeterRateType,
        scale: int,
        value: float | None,
        delta_time: int | None,
        previous_value: float | None,
    ) -> None:
        self._parent_device: QolsysMeterDevice = parent_device
        self._meter_type: MeterType = meter_type
        self._rate_type: MeterRateType = rate_type
        self._scale: int = scale
        self._value: float | None = value
        self._delta_time: int | None = delta_time
        self._previous_value: float | None = previous_value

    @property
    def previous_value(self) -> float | None:
        return self._previous_value

    @previous_value.setter
    def previous_value(self, value: float | None) -> None:
        if self.previous_value != value:
            self._previous_value = value
            LOGGER.debug(
                "ZWaveMeter%s (%s) - %s - previous_value: %s",
                self._parent_device.node_id,
                self._parent_device.node_name,
                self.meter_type.name,
                value,
            )
            self._parent_device.notify()

    @property
    def delta_time(self) -> int | None:
        return self._delta_time

    @delta_time.setter
    def delta_time(self, value: int | None) -> None:
        if self.delta_time != value:
            self._delta_time = value
            LOGGER.debug(
                "ZWaveMeter%s (%s) - %s - delta_time: %s",
                self._parent_device.node_id,
                self._parent_device.node_name,
                self.meter_type.name,
                value,
            )
            self._parent_device.notify()

    @property
    def scale(self) -> int:
        return self._scale

    @scale.setter
    def scale(self, value: int) -> None:
        if self._scale != value:
            self._scale = value
            self._parent_device.notify()

    @property
    def rate_type(self) -> MeterRateType:
        return self._rate_type

    @rate_type.setter
    def rate_type(self, value: MeterRateType) -> None:
        if self.rate_type != value:
            self._rate_type = value
            LOGGER.debug(
                "ZWaveMeter%s (%s) - %s - rate_type: %s",
                self._parent_device.node_id,
                self._parent_device.node_name,
                self.meter_type.name,
                value.name,
            )
            self._parent_device.notify()

    @property
    def meter_type(self) -> MeterType:
        return self._meter_type

    @meter_type.setter
    def meter_type(self, value: MeterType) -> None:
        if self.meter_type != value:
            LOGGER.error("meter_type cannot change once meter_device is created")
            self._parent_device.notify()

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, new_value: float | None) -> None:
        if self.value != new_value:
            self._value = new_value

            scale_type: type[IntEnum] = self._parent_device.scale_for_meter_type(self.meter_type)

            LOGGER.debug(
                "ZWaveMeter%s (%s) - %s - value: %s (%s)",
                self._parent_device.node_id,
                self._parent_device.node_name,
                self.meter_type.name,
                new_value,
                scale_type(self._scale).name,
            )
            self._parent_device.notify()


class QolsysMeterDevice(QolsysZWaveDevice):
    def __init__(self, zwave_dict: dict[str, str]) -> None:
        super().__init__(zwave_dict)

        self._meters: list[QolsysMeterSensor] = []

    @property
    def meters(self) -> list[QolsysMeterSensor]:
        return self._meters

    def create_generic_electric_meter(self) -> None:
        for type in ZWaveElectricMeterScale:
            qolsys_meter_sensor = QolsysMeterSensor(
                self,
                MeterType.ELECTRIC_METER,
                MeterRateType.IMPORT,
                type,
                None,
                None,
                None,
            )
            self.add_meter(qolsys_meter_sensor)

    def add_meter(self, new_meter: QolsysMeterSensor) -> None:
        if self.meter(new_meter.meter_type, new_meter.scale) is not None:
            LOGGER.error("Error Adding Meter, meter_type allready present")
            return

        self.meters.append(new_meter)
        self.notify()

    def meter(self, meter_type: MeterType, scale: int) -> QolsysMeterSensor | None:
        for meter in self.meters:
            if meter.meter_type == meter_type and meter.scale == scale:
                return meter
        return None

    def scale_for_meter_type(self, meter_type: MeterType) -> type[IntEnum]:
        match meter_type:
            case MeterType.ELECTRIC_METER:
                return ZWaveElectricMeterScale

            case MeterType.GAZ_METER:
                return ZWaveGasMeterScale

            case MeterType.WATER_METER:
                return ZWaveWaterMeterScale

            case MeterType.COOLING:
                return ZWaveThermalMeterScale

            case MeterType.HEATING:
                return ZWaveThermalMeterScale

        return ZWaveUnknownMeterScale

    def update_raw(self, payload: bytes) -> None:
        LOGGER.debug("Raw Update (node%s) - payload:(%s)", self.node_id, payload.hex())

        try:
            command_class = payload[0]
            command = payload[1]

        except (ValueError, IndexError) as err:
            LOGGER.error("No Z-Wave payload command_class or command (%s): (%s)", err, payload.hex())
            return

        if command is not ZwaveCommand.GET.value or command_class is not ZwaveCommandClass.Meter.value:
            LOGGER.warning("Invalid Z-Wave payload command_class or command: (%s)", payload.hex())
            return

        try:
            props1 = payload[2]
            props2 = payload[3]
        except ValueError as err:
            LOGGER.error("Missings payload information (props1 and props2)(%s): (%s)", err, payload.hex())
            return

        meter_type = MeterType.UNKNOWN
        try:
            meter_type = MeterType(props1 & 0x1F)
        except ValueError:
            LOGGER.error("Unknown ZWave MeterType, Setting to RESERVED")
            meter_type = MeterType.RESERVED

        rate_type = MeterRateType.UNSPECIFIED
        try:
            rate_type = MeterRateType((props1 >> 5) & 0x03)
        except ValueError:
            LOGGER.error("Unknown ZWave MeterRateType, Setting to UNSPECIFIED")
            rate_type = MeterRateType.UNSPECIFIED

        precision = (props2 >> 5) & 0x07
        scale_msb = (props1 >> 7) & 0x01
        scale_lsb = (props2 >> 3) & 0x03
        size = props2 & 0x07

        scale = (scale_msb << 2) | scale_lsb

        value: float | None = None
        try:
            value_bytes = payload[4 : 4 + size]
            raw_value = int.from_bytes(value_bytes, byteorder="big", signed=False)
            value = raw_value / (10**precision)
        except ValueError:
            LOGGER.warning("ZWaveMeter: Value Error")

        delta_time: int = 0
        try:
            offset = 4 + size
            delta_time = int.from_bytes(payload[offset : offset + 2], "big")
            offset += 2
        except ValueError:
            LOGGER.warning("delta_time: Value Error")

        prev_value: float | None = None
        try:
            if len(payload) >= offset + size:
                prev_raw = int.from_bytes(payload[offset : offset + size], "big")
                prev_value = prev_raw / (10**precision)
        except ValueError:
            LOGGER.warning("previous_value: Value Error")

        # Update existing meter or add new meter
        scale_type = self.scale_for_meter_type(meter_type)
        meter = self.meter(meter_type, scale_type(scale))
        if meter is not None:
            self.start_batch_update()
            meter.scale = scale_type(scale)
            meter.value = value
            meter.delta_time = delta_time
            meter.previous_value = prev_value
            meter.rate_type = rate_type
            self.end_batch_update()

        if meter is None:
            new_meter = QolsysMeterSensor(self, meter_type, rate_type, scale, value, delta_time, prev_value)
            self.add_meter(new_meter)
