"""Tests for ValveServiceZwave command dispatch and state decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

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
    async def test_open_when_closed_sends_binary_set_true(self) -> None:
        service, device = _make(is_closed=True, endpoint=4)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "4", True)

    @pytest.mark.asyncio
    async def test_close_when_open_sends_binary_set_false(self) -> None:
        service, device = _make(is_closed=False, endpoint=4)
        await service.close()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "4", False)

    @pytest.mark.asyncio
    async def test_open_when_already_open_is_noop(self) -> None:
        service, device = _make(is_closed=False)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_close_when_already_closed_is_noop(self) -> None:
        service, device = _make(is_closed=True)
        await service.close()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_open_without_binary_support_does_not_dispatch(self) -> None:
        service, device = _make(supports_binary=False, is_closed=True)
        await service.open()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    def test_update_marks_closed_when_status_closed(self) -> None:
        service, _ = _make(is_closed=False, status="Closed")
        service.update_automation_service()
        assert service.is_closed is True

    def test_update_marks_open_when_status_open(self) -> None:
        service, _ = _make(is_closed=True, status="open")
        service.update_automation_service()
        assert service.is_closed is False
