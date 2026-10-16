"""Tests for SensorServiceZwave multilevel-sensor decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_sensor import SensorServiceZwave
from qolsys_controller.enum_qolsys import QolsysSensorScale

from .zwave_service_helpers import make_zwave_device


def _make(endpoint: int = 0) -> tuple[SensorServiceZwave, MagicMock]:
    device = make_zwave_device()
    # Humidity path looks for a thermostat on the same endpoint; keep it absent.
    device.service_get.return_value = None
    return SensorServiceZwave(automation_device=device, endpoint=endpoint), device


class TestSensorServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "SensorService"

    def test_air_temperature_creates_fahrenheit_sensor(self) -> None:
        service, _ = _make()
        service.update_zwave_service({"AIR TEMPERATURE": {"Fahrenheit (F)": 72.5}})
        sensor = service.sensor(QolsysSensorScale.TEMPERATURE_FAHRENHEIT)
        assert sensor is not None
        assert sensor.value == 72.5

    def test_humidity_creates_relative_humidity_sensor(self) -> None:
        service, _ = _make()
        service.update_zwave_service({"HUMIDITY": {"Percentage value (%)": 45.0}})
        sensor = service.sensor(QolsysSensorScale.RELATIVE_HUMIDITY)
        assert sensor is not None
        assert sensor.value == 45.0

    def test_repeated_update_reuses_sensor_and_updates_value(self) -> None:
        service, _ = _make()
        service.update_zwave_service({"AIR TEMPERATURE": {"Fahrenheit (F)": 70.0}})
        service.update_zwave_service({"AIR TEMPERATURE": {"Fahrenheit (F)": 68.0}})
        temp_sensors = [s for s in service.sensors if s.unit == QolsysSensorScale.TEMPERATURE_FAHRENHEIT]
        assert len(temp_sensors) == 1
        assert temp_sensors[0].value == 68.0

    def test_unrelated_key_is_ignored(self) -> None:
        service, _ = _make()
        service.update_zwave_service({"LUMINANCE": {"Lux": 500}})
        assert service.sensors == []
