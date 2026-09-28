"""Tests for CoverServiceADC command dispatch and state decoding."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_adc.service_cover import CoverServiceADC
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType


def _make_mock_device() -> MagicMock:
    device = MagicMock()
    device.virtual_node_id = "42"
    device.device_name = "Garage Door"
    device.protocol.name = "ADC"
    device.controller = MagicMock()
    device.controller.commands.adc.virtual_device_action = AsyncMock()
    device.to_dict_event.return_value = {}
    return device


def _make(endpoint: int = 1) -> tuple[CoverServiceADC, MagicMock]:
    device = _make_mock_device()
    return CoverServiceADC(automation_device=device, endpoint=endpoint), device


class TestCoverServiceADC:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "CoverService"

    def test_capabilities(self) -> None:
        service, _ = _make()
        assert service.supports_open() is True
        assert service.supports_close() is True
        assert service.supports_stop() is False
        assert service.supports_position() is False

    def test_func_type_unknown_before_update(self) -> None:
        service, _ = _make()
        assert service.func_type == vdFuncType.UNKNOWN

    @pytest.mark.asyncio
    async def test_open_sends_on(self) -> None:
        service, device = _make()
        await service.open()
        device.controller.commands.adc.virtual_device_action.assert_awaited_once_with("42", 1, vdFuncState.ON)

    @pytest.mark.asyncio
    async def test_close_sends_off(self) -> None:
        service, device = _make()
        await service.close()
        device.controller.commands.adc.virtual_device_action.assert_awaited_once_with("42", 1, vdFuncState.OFF)

    @pytest.mark.asyncio
    async def test_open_emits_transient_update_then_settles(self) -> None:
        # By design, open() pulses is_opening=True (emitting an AUTOMATION_UPDATE
        # to observers) and then resets it. The transient notify is expected;
        # the service settles back to is_opening=False.
        service, device = _make()
        await service.open()
        device.notify.assert_called()  # transient "opening" signal was emitted
        assert service.is_opening is False  # ...and state settles back

    @pytest.mark.asyncio
    async def test_close_emits_transient_update_then_settles(self) -> None:
        # Mirror of open(): close() pulses is_closing=True then resets it.
        service, device = _make()
        await service.close()
        device.notify.assert_called()  # transient "closing" signal was emitted
        assert service.is_closing is False  # ...and state settles back

    def test_update_adc_service_closed(self) -> None:
        service, _ = _make()
        service.update_adc_service(
            local_control=vdFuncLocalControl.FULL_CONTROL,
            func_name=vdFuncName.OPEN_CLOSE,
            func_type=vdFuncType.BINARY_ACTUATOR,
            func_state=vdFuncState.OFF,
            timestamp="0",
        )
        assert service.is_closed is True
        assert service.func_type == vdFuncType.BINARY_ACTUATOR

    def test_update_adc_service_open(self) -> None:
        service, _ = _make()
        service._is_closed = True
        service.update_adc_service(
            local_control=vdFuncLocalControl.FULL_CONTROL,
            func_name=vdFuncName.OPEN_CLOSE,
            func_type=vdFuncType.BINARY_ACTUATOR,
            func_state=vdFuncState.ON,
            timestamp="0",
        )
        assert service.is_closed is False

    def test_to_dict_event(self) -> None:
        service, _ = _make()
        service._is_closed = True
        result = service.to_dict_event()
        assert result["service_type"] == "CoverService"
        assert result["state"]["is_closed"] is True
        assert result["capabilities"]["supports_open"] is True
