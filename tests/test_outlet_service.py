"""Tests for OutletService and OutletServiceZwave."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_zwave.service_outlet import OutletServiceZwave
from qolsys_controller.enum_zwave import ZwaveCommandClass


def _make_mock_device() -> MagicMock:
    device = MagicMock()
    device.virtual_node_id = "8"
    device.device_name = "Smart Plug"
    device.protocol.name = "ZWAVE"
    device.controller = MagicMock()
    device.controller.commands.zwave.switch_binary_set = AsyncMock()
    device.status = "off"
    device.command_class_list = [ZwaveCommandClass.SwitchBinary]
    device.to_dict_event.return_value = {}
    return device


class TestOutletServiceZwave:
    def test_update_status_on(self) -> None:
        device = _make_mock_device()
        device.status = "on"
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service.update_automation_service()
        assert service.is_on is True

    @pytest.mark.asyncio
    async def test_turn_on(self) -> None:
        device = _make_mock_device()
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service._is_on = False
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("8", "0", True)

    @pytest.mark.asyncio
    async def test_turn_on_sends_even_when_already_on(self) -> None:
        # turn_on no longer short-circuits on state; it always sends the command.
        device = _make_mock_device()
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service._is_on = True
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_awaited_once_with("8", "0", True)

    @pytest.mark.asyncio
    async def test_turn_on_skips_when_command_class_unsupported(self) -> None:
        # The real gate is now SwitchBinary support, not the is_on state.
        device = _make_mock_device()
        device.command_class_list = []
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        await service.turn_on()
        device.controller.commands.zwave.switch_binary_set.assert_not_awaited()

    def test_is_on_notifies(self) -> None:
        device = _make_mock_device()
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service.is_on = True
        device.notify.assert_called_once()

    def test_to_dict_event(self) -> None:
        device = _make_mock_device()
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service._is_on = True
        result = service.to_dict_event()
        assert result["service_type"] == "OutletService"
        assert result["state"]["is_on"] is True
