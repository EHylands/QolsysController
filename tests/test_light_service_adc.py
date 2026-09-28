"""Tests for LightServiceADC command dispatch and state decoding."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_adc.service_light import LightServiceADC
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType


def _make_mock_device() -> MagicMock:
    device = MagicMock()
    device.virtual_node_id = "42"
    device.device_name = "Porch Light"
    device.protocol.name = "ADC"
    device.controller = MagicMock()
    device.controller.commands.adc.virtual_device_action = AsyncMock()
    device.to_dict_event.return_value = {}
    return device


def _make(endpoint: int = 3) -> tuple[LightServiceADC, MagicMock]:
    device = _make_mock_device()
    return LightServiceADC(automation_device=device, endpoint=endpoint), device


class TestLightServiceADC:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "LightService"

    def test_supports_level_false(self) -> None:
        service, _ = _make()
        assert service.supports_level() is False

    def test_func_type_unknown_before_update(self) -> None:
        service, _ = _make()
        assert service.func_type == vdFuncType.UNKNOWN

    @pytest.mark.asyncio
    async def test_turn_on(self) -> None:
        service, device = _make()
        await service.turn_on()
        device.controller.commands.adc.virtual_device_action.assert_awaited_once_with("42", 3, vdFuncState.ON)

    @pytest.mark.asyncio
    async def test_turn_off(self) -> None:
        service, device = _make()
        await service.turn_off()
        device.controller.commands.adc.virtual_device_action.assert_awaited_once_with("42", 3, vdFuncState.OFF)

    def test_update_adc_service_turns_on(self) -> None:
        service, _ = _make()
        service.update_adc_service(
            local_control=vdFuncLocalControl.STATUS_ONLY,
            func_name=vdFuncName.OFF_ON,
            func_type=vdFuncType.LIGHT,
            func_state=vdFuncState.ON,
            timestamp="0",
        )
        assert service.is_on is True
        assert service.func_type == vdFuncType.LIGHT

    def test_update_adc_service_turns_off(self) -> None:
        service, _ = _make()
        service._is_on = True
        service.update_adc_service(
            local_control=vdFuncLocalControl.STATUS_ONLY,
            func_name=vdFuncName.OFF_ON,
            func_type=vdFuncType.LIGHT,
            func_state=vdFuncState.OFF,
            timestamp="0",
        )
        assert service.is_on is False

    def test_to_dict_event(self) -> None:
        service, _ = _make()
        service._is_on = True
        result = service.to_dict_event()
        assert result["type"] == "LightService"
        assert result["state"]["is_on"] is True
        assert result["capabilities"]["supports_level"] is False
