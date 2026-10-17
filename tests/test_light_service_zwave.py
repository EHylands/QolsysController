"""Tests for LightServiceZwave state decoding from the panel extras refresh."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_light import LightServiceZwave


def _make_mock_device(status: str = "on", extras: str = '{"LEVEL": "60"}') -> MagicMock:
    device = MagicMock()
    device.virtual_node_id = "6"
    device.device_name = "Living Room Dimmer"
    device.protocol.name = "ZWAVE"
    device.status = status
    device.extras = extras
    device.to_dict_event.return_value = {}
    return device


def _make(status: str = "on", extras: str = '{"LEVEL": "60"}', endpoint: int = 0) -> tuple[LightServiceZwave, MagicMock]:
    device = _make_mock_device(status, extras)
    return LightServiceZwave(automation_device=device, endpoint=endpoint), device


class TestLightServiceZwaveExtrasRefresh:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "LightService"

    def test_update_reads_level_from_extras_when_on(self) -> None:
        service, _ = _make(status="on", extras='{"LEVEL": "60"}')
        service.update_automation_service()
        assert service.is_on is True
        assert service.level == 60

    def test_update_reports_zero_when_off_despite_stale_extras(self) -> None:
        # The panel keeps extras["LEVEL"] at the last on-level even while off.
        service, _ = _make(status="off", extras='{"LEVEL": "60"}')
        service.update_automation_service()
        assert service.is_on is False
        assert service.level == 0

    def test_off_refresh_does_not_clobber_live_zero(self) -> None:
        # Regression for the 60 -> 0 -> 60 bounce: a live SwitchMultilevel report
        # (2603000000) sets level 0 when the dimmer turns off; the subsequent panel
        # DB refresh (status off, extras still LEVEL=60) must not restore 60.
        service, device = _make(status="on", extras='{"LEVEL": "60"}')
        service.update_automation_service()
        assert service.level == 60

        # Live raw report says the dimmer output is now 0 (parse_command_26).
        service.level = 0

        # Panel DB update arrives: now off, but extras LEVEL is still the stale 60.
        device.status = "off"
        service.update_automation_service()

        assert service.is_on is False
        assert service.level == 0

    def test_malformed_extras_does_not_raise(self) -> None:
        service, _ = _make(status="on", extras="not-json")
        service.update_automation_service()  # should log an error, not raise
