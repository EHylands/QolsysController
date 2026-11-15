"""Tests for QolsysZone — property setters, update parsing, and PowerG attributes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.enum_qolsys import QolsysNotification, ZoneSensorType, ZoneStatus
from qolsys_controller.observable import Event
from qolsys_controller.zone import QolsysZone

UNAVAILABLE_STATUSES = {
    ZoneStatus.UNREACHABLE,
    ZoneStatus.FAILURE,
    ZoneStatus.NOT_NETWORKED,
    ZoneStatus.TROUBLE,
    ZoneStatus.SYNCHRONIZING,
    ZoneStatus.DISCONNECTED,
    ZoneStatus.TAMPERED,
    ZoneStatus.UNKNOWN,
}


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


class TestIsOn:
    @pytest.mark.parametrize(
        "status",
        [
            "Open",
            "Alarmed",
            "Activated",
            "Inactive",
            "Occupied",
            "Auxiliary Emergency",
            "Fire Emergency",
            "Police Emergency",
            "Silent Auxiliary Emergency",
            "Silent Police Emergency",
            "High Temp Alert",
        ],
    )
    def test_on_statuses(self, status: str) -> None:
        assert _make_zone({"sensorstatus": status}).is_on() is True

    @pytest.mark.parametrize("status", ["Closed", "Active", "Idle", "Unreachable", "Synchronizing", "Tampered"])
    def test_off_statuses(self, status: str) -> None:
        assert _make_zone({"sensorstatus": status}).is_on() is False


class TestIsTrouble:
    @pytest.mark.parametrize("status", ["Unreachable", "Failure", "Not Networked", "Trouble", "Synchronizing", "disconnected"])
    def test_trouble_statuses(self, status: str) -> None:
        assert _make_zone({"sensorstatus": status}).is_trouble() is True

    @pytest.mark.parametrize("status", ["Open", "Closed", "Active", "Idle", "Tampered"])
    def test_non_trouble_statuses(self, status: str) -> None:
        assert _make_zone({"sensorstatus": status}).is_trouble() is False


class TestIsTampered:
    def test_tampered_status(self) -> None:
        assert _make_zone({"sensorstatus": "Tampered"}).is_tampered() is True

    @pytest.mark.parametrize("status", ["Open", "Closed", "Idle", "Unreachable", "Trouble", "Failure"])
    def test_non_tampered_statuses(self, status: str) -> None:
        assert _make_zone({"sensorstatus": status}).is_tampered() is False

    def test_unparseable_status_is_not_tampered(self) -> None:
        zone = _make_zone({"sensorstatus": "SomeNewStatus"})
        assert zone.sensorstatus == ZoneStatus.UNKNOWN
        assert zone.is_tampered() is False


class TestIsAvailable:
    @pytest.mark.parametrize("status", list(ZoneStatus), ids=lambda s: s.name)
    def test_availability_for_every_status(self, status: ZoneStatus) -> None:
        zone = _make_zone({"sensorstatus": status.value})
        assert zone.is_available() is (status not in UNAVAILABLE_STATUSES)

    def test_unparseable_status_is_unavailable(self) -> None:
        zone = _make_zone({"sensorstatus": "SomeNewStatus"})
        assert zone.sensorstatus == ZoneStatus.UNKNOWN
        assert zone.is_trouble() is False
        assert zone.is_available() is False

    def test_recovers_from_unknown_on_update(self) -> None:
        zone = _make_zone({"sensorstatus": "SomeNewStatus"})
        zone.update({"zoneid": "1", "sensorstatus": "Closed"})
        assert zone.is_available() is True

    def test_tampered_is_unavailable_but_not_trouble(self) -> None:
        zone = _make_zone({"sensorstatus": "Tampered"})
        assert zone.is_trouble() is False
        assert zone.is_available() is False

    def test_becomes_unavailable_then_recovers_on_update(self) -> None:
        zone = _make_zone()
        assert zone.is_available() is True

        zone.update({"zoneid": "1", "sensorstatus": "Unreachable"})
        assert zone.is_available() is False

        zone.update({"zoneid": "1", "sensorstatus": "Closed"})
        assert zone.is_available() is True

    def test_recovers_from_tamper_on_update(self) -> None:
        zone = _make_zone({"sensorstatus": "Tampered"})
        zone.update({"zoneid": "1", "sensorstatus": "Open"})
        assert zone.is_available() is True
        assert zone.is_on() is True

    def test_unknown_status_update_keeps_previous_availability(self) -> None:
        zone = _make_zone({"sensorstatus": "Unreachable"})
        zone.update({"zoneid": "1", "sensorstatus": "SomeNewStatus"})
        assert zone.sensorstatus == ZoneStatus.UNREACHABLE
        assert zone.is_available() is False

    def test_availability_change_notifies_observers(self) -> None:
        zone = _make_zone()
        events: list[Event] = []
        zone.register(QolsysNotification.ZONE_UPDATE, events.append)

        zone.update({"zoneid": "1", "sensorstatus": "Tampered"})

        assert len(events) == 1
        assert events[0].data["state"]["status"] == "tampered"
        assert events[0].source is zone
        assert zone.is_available() is False


class TestSafetyZones:
    @pytest.mark.parametrize("group", ["co", "freeze", "Freeze_Non_Reporting"])
    def test_life_safety_groups_cannot_be_bypassed(self, group: str) -> None:
        zone = _make_zone({"sensorgroup": group})
        assert zone.is_safety() is True
        assert zone.is_bypassable() is False

    def test_extras_bypass_enabled_overrules_safety(self) -> None:
        zone = _make_zone({"sensorgroup": "co"})
        zone._extras = '{"BYPASS": "Enabled"}'
        assert zone.is_bypassable() is True

    def test_regular_group_stays_bypassable(self) -> None:
        zone = _make_zone()
        assert zone.is_safety() is False
        assert zone.is_bypassable() is True
