"""Tests for QolsysZone — property setters, update parsing, and PowerG attributes."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.enum_qolsys import ZoneSensorType
from qolsys_controller.zone import QolsysZone


def _make_settings(**overrides: object) -> MagicMock:
    settings = MagicMock()
    settings.motion_sensor_delay = False
    settings.motion_sensor_delay_sec = 310
    for k, v in overrides.items():
        setattr(settings, k, v)
    return settings


def _make_zone(data: dict[str, str] | None = None, **kw: object) -> QolsysZone:
    defaults: dict[str, str] = {
        "zoneid": "1",
        "sensorname": "Front Door",
        "sensorstatus": "Closed",
        "sensortype": "Door_Window",
        "sensorgroup": "entryexitdelay",
        "partition_id": "0",
    }
    if data:
        defaults.update(data)
    return QolsysZone(defaults, _make_settings(**kw))


class TestZoneSetters:
    def test_set_partition_id(self) -> None:
        zone = _make_zone()
        zone.partition_id = "1"
        assert zone.partition_id == "1"

    def test_latestdBm_out_of_range(self) -> None:
        zone = _make_zone({"latestdBm": "999"})
        assert zone.latestdBm is None


class TestZoneUpdate:
    def test_update_sensortts(self) -> None:
        zone = _make_zone()
        zone.update({"zoneid": "1", "sensortts": "12345"})
        assert zone._sensortts == "12345"

    def test_update_wrong_zone_id_ignored(self) -> None:
        zone = _make_zone()
        zone.update({"zoneid": "999", "sensorname": "Hacked"})
        assert zone.sensorname == "Front Door"


class TestPowerg:
    def test_extras_bad_json_ignored(self) -> None:
        zone = _make_zone({"shortID": "42"})
        zone.update_powerg({"shortID": "42", "extras": "not-json"})
        assert zone._powerg_extras == ""

    def test_temperature_rounding(self) -> None:
        zone = _make_zone()
        zone._powerg_temperature = "22.456"
        assert zone.powerg_temperature == 22.5

    def test_battery_voltage_millivolts(self) -> None:
        zone = _make_zone()
        zone._powerg_battery_voltage = "3200"
        assert zone.powerg_battery_voltage == 3.2


class TestUnknownSensorType:
    def test_unknown_type_defaults(self) -> None:
        zone = _make_zone({"sensortype": "SomeNewType"})
        assert zone.sensortype == ZoneSensorType.UNKNOWN
