"""Tests for StatusServiceZwave node-status decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_status import StatusServiceZwave

from .zwave_service_helpers import make_zwave_device


def _make(*, node_status: str = "normal", endpoint: int = 0) -> tuple[StatusServiceZwave, MagicMock]:
    # update_automation_service does isinstance(device, QolsysAutomationDeviceZwave) -> spec=True
    device = make_zwave_device(spec=True)
    device.node_status = node_status
    return StatusServiceZwave(automation_device=device, endpoint=endpoint), device


class TestStatusServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "StatusService"

    def test_supports_status_true(self) -> None:
        service, _ = _make()
        assert service.supports_status() is True

    def test_normal_status_not_malfunctioning(self) -> None:
        service, _ = _make(node_status="Normal")
        service.update_automation_service()
        assert service.is_malfunctioning is False

    def test_non_normal_status_is_malfunctioning(self) -> None:
        service, _ = _make(node_status="failed")
        service.update_automation_service()
        assert service.is_malfunctioning is True
