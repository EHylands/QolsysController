"""Tests for OutletServiceZwave command dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.automation_zwave.service_outlet import OutletServiceZwave
from qolsys_controller.enum_zwave import ZwaveCommandClass

from .zwave_service_helpers import make_zwave_device


def _make(
    *,
    supports_binary: bool = True,
    endpoint: int = 0,
) -> tuple[OutletServiceZwave, MagicMock]:
    command_classes = [ZwaveCommandClass.SwitchBinary] if supports_binary else []
    device = make_zwave_device(command_classes=command_classes)
    return OutletServiceZwave(automation_device=device, endpoint=endpoint), device


class TestOutletServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "OutletService"

    @pytest.mark.asyncio
    async def test_turn_on_sends_binary_set_true(self) -> None:
        service, device = _make(endpoint=2)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "2", True)

    @pytest.mark.asyncio
    async def test_turn_off_sends_binary_set_false(self) -> None:
        service, device = _make(endpoint=2)
        await service.turn_off()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "2", False)

    @pytest.mark.asyncio
    async def test_turn_on_without_binary_support_does_not_dispatch(self) -> None:
        service, device = _make(supports_binary=False)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_turn_off_without_binary_support_does_not_dispatch(self) -> None:
        service, device = _make(supports_binary=False)
        await service.turn_off()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()
