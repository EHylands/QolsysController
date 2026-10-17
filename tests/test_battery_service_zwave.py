"""Tests for BatteryServiceZwave capability checks and level decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_battery import BatteryServiceZwave

from .zwave_service_helpers import make_zwave_device


def _make(*, battery_value: str = "80", endpoint: int = 0) -> tuple[BatteryServiceZwave, MagicMock]:
    device = make_zwave_device()
    # supports_battery_level reads the private attr; update_* reads the property.
    device._node_battery_level_value = battery_value
    device.node_battery_level_value = battery_value
    return BatteryServiceZwave(automation_device=device, endpoint=endpoint), device


class TestBatteryServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "BatteryService"

    def test_supports_battery_low_always_false(self) -> None:
        service, _ = _make()
        assert service.supports_battery_low() is False

    def test_supports_battery_level_true_for_valid_value(self) -> None:
        service, _ = _make(battery_value="80")
        assert service.supports_battery_level() is True

    def test_supports_battery_level_false_for_empty_value(self) -> None:
        service, _ = _make(battery_value="")
        assert service.supports_battery_level() is False

    def test_supports_battery_level_false_for_out_of_range(self) -> None:
        service, _ = _make(battery_value="150")
        assert service.supports_battery_level() is False

    def test_update_sets_battery_level(self) -> None:
        service, _ = _make(battery_value="80")
        service.update_automation_service()
        assert service.battery_level == 80

    def test_is_disabled_when_level_unavailable(self) -> None:
        service, _ = _make(battery_value="")
        assert service.is_disabled is True
        service.update_automation_service()
        assert service.battery_level is None
