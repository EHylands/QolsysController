"""Tests for SirenServiceZwave command dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.automation_zwave.service_siren import SirenServiceZwave
from qolsys_controller.enum_zwave import ZwaveCommandClass

from .zwave_service_helpers import make_zwave_device


def _make(
    *,
    supports_binary: bool = True,
    is_on: bool = False,
    endpoint: int = 0,
) -> tuple[SirenServiceZwave, MagicMock]:
    command_classes = [ZwaveCommandClass.SwitchBinary] if supports_binary else []
    device = make_zwave_device(command_classes=command_classes)
    service = SirenServiceZwave(automation_device=device, endpoint=endpoint)
    service._is_on = is_on
    return service, device


class TestSirenServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "SirenService"

    @pytest.mark.asyncio
    async def test_turn_on_when_off_sends_binary_set_true(self) -> None:
        service, device = _make(is_on=False, endpoint=1)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "1", True)

    @pytest.mark.asyncio
    async def test_turn_off_when_on_sends_binary_set_false(self) -> None:
        service, device = _make(is_on=True, endpoint=1)
        await service.turn_off()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("6", "1", False)

    @pytest.mark.asyncio
    async def test_turn_on_when_already_on_is_noop(self) -> None:
        service, device = _make(is_on=True)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_turn_off_when_already_off_is_noop(self) -> None:
        service, device = _make(is_on=False)
        await service.turn_off()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_turn_on_without_binary_support_does_not_dispatch(self) -> None:
        service, device = _make(supports_binary=False, is_on=False)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()
