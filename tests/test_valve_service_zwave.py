"""Tests for ValveServiceZwave command dispatch and state decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave
from qolsys_controller.automation_zwave.service_valve import ValveServiceZwave
from qolsys_controller.enum_zwave import ZwaveCommandClass

from .zwave_service_helpers import make_zwave_device


def _make(
    *,
    supports_binary: bool = True,
    is_closed: bool = False,
    status: str = "open",
    endpoint: int = 0,
) -> tuple[ValveServiceZwave, MagicMock]:
    command_classes = [ZwaveCommandClass.SwitchBinary] if supports_binary else []
    device = make_zwave_device(command_classes=command_classes, status=status)
    service = ValveServiceZwave(automation_device=device, endpoint=endpoint)
    service._is_closed = is_closed
    return service, device


class TestValveServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "ValveService"

    def test_capabilities(self) -> None:
        service, _ = _make()
        assert service.supports_open() is True
        assert service.supports_close() is True
        assert service.supports_stop() is False
        assert service.supports_position() is False

    @pytest.mark.asyncio
    async def test_open_when_closed_sends_binary_set_false(self) -> None:
        service, device = _make(is_closed=True, endpoint=4)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "4", False)

    @pytest.mark.asyncio
    async def test_close_when_open_sends_binary_set_true(self) -> None:
        service, device = _make(is_closed=False, endpoint=4)
        await service.close()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "4", True)

    @pytest.mark.asyncio
    async def test_open_when_already_open_still_sends_command(self) -> None:
        service, device = _make(is_closed=False)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "0", False)

    @pytest.mark.asyncio
    async def test_close_when_already_closed_still_sends_command(self) -> None:
        service, device = _make(is_closed=True)
        await service.close()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "0", True)

    @pytest.mark.asyncio
    async def test_open_without_binary_support_does_not_dispatch(self) -> None:
        service, device = _make(supports_binary=False, is_closed=True)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    def test_update_marks_closed_when_status_closed(self) -> None:
        service, _ = _make(is_closed=False, status="Close")
        service.update_automation_service()
        assert service.is_closed is True

    def test_update_marks_open_when_status_open(self) -> None:
        service, _ = _make(is_closed=True, status="open")
        service.update_automation_service()
        assert service.is_closed is False

    @pytest.mark.parametrize("status", ["", "Closed", "Unknown"])
    @pytest.mark.parametrize("is_closed", [True, False])
    def test_update_ignores_and_warns_on_other_status(
        self, status: str, is_closed: bool, caplog: pytest.LogCaptureFixture
    ) -> None:
        service, _ = _make(is_closed=is_closed, status=status)
        service.update_automation_service()
        assert service.is_closed is is_closed
        assert "Unexpected valve status" in caplog.text

    @pytest.mark.parametrize("status", ["Open", "Close"])
    def test_update_does_not_warn_on_known_status(self, status: str, caplog: pytest.LogCaptureFixture) -> None:
        service, _ = _make(status=status)
        service.update_automation_service()
        assert "Unexpected valve status" not in caplog.text

    @pytest.mark.parametrize(("value", "expected"), [(0x00, False), (0xFF, True)])
    def test_switch_binary_report_sets_state(self, value: int, expected: bool) -> None:
        service, device = _make(is_closed=not expected)
        device.service_get.return_value = service
        QolsysAutomationDeviceZwave.parse_command_25(device, bytes([0x25, 0x03, value, value, 0x00]), 0)
        assert service.is_closed is expected

    @pytest.mark.parametrize("is_closed", [True, False])
    def test_switch_binary_report_ignores_unknown_value(self, is_closed: bool) -> None:
        service, device = _make(is_closed=is_closed)
        device.service_get.return_value = service
        QolsysAutomationDeviceZwave.parse_command_25(device, bytes.fromhex("2503FEFE00"), 0)
        assert service.is_closed is is_closed
        device.service_add.assert_not_called()
