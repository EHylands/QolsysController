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
    device.controller.command_zwave_switch_binary_set = AsyncMock()
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
        device.controller.command_zwave_switch_binary_set.assert_awaited_once_with("8", "0", True)

    @pytest.mark.asyncio
    async def test_turn_on_already_on_skips(self) -> None:
        device = _make_mock_device()
        service = OutletServiceZwave(automation_device=device, endpoint=0)
        service._is_on = True
        await service.turn_on()
        device.controller.command_zwave_switch_binary_set.assert_not_awaited()

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
