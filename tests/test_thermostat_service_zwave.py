"""Tests for ThermostatServiceZwave command dispatch."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_zwave.service_thermostat import ThermostatServiceZwave
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode
from qolsys_controller.enum_zwave import ThermostatFanMode, ThermostatMode, ThermostatSetpointMode


def _make_mock_device() -> MagicMock:
    device = MagicMock()
    device.virtual_node_id = "8"
    device.device_name = "Hallway Thermostat"
    device.protocol.name = "ZWAVE"
    device.controller = MagicMock()
    device.controller.commands.zwave.thermostat_mode_set = AsyncMock()
    device.controller.commands.zwave.thermostat_setpoint_set = AsyncMock()
    device.controller.commands.zwave.thermostat_fan_mode_set = AsyncMock()
    device.to_dict_event.return_value = {}
    return device


def _make(endpoint: int = 0) -> tuple[ThermostatServiceZwave, MagicMock]:
    # Return the mock device too: assert on it directly so mypy sees MagicMock
    # (Any) rather than the real, typed automation_device (no mock assertions).
    device = _make_mock_device()
    return ThermostatServiceZwave(automation_device=device, endpoint=endpoint), device


class TestThermostatServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "ThermostatServiceZwave"

    @pytest.mark.asyncio
    async def test_turn_off_sends_mode_off(self) -> None:
        service, device = _make()
        await service.turn_off()
        device.controller.commands.zwave.thermostat_mode_set.assert_awaited_once_with("8", "0", ThermostatMode.OFF)

    @pytest.mark.asyncio
    async def test_set_hvac_mode_heat(self) -> None:
        service, device = _make()
        await service.set_hvac_mode(QolsysHvacMode.HEAT)
        device.controller.commands.zwave.thermostat_mode_set.assert_awaited_once_with("8", "0", ThermostatMode.HEAT)

    @pytest.mark.asyncio
    async def test_set_hvac_mode_cool(self) -> None:
        service, device = _make()
        await service.set_hvac_mode(QolsysHvacMode.COOL)
        device.controller.commands.zwave.thermostat_mode_set.assert_awaited_once_with("8", "0", ThermostatMode.COOL)

    @pytest.mark.asyncio
    async def test_set_fan_mode_high(self) -> None:
        service, device = _make()
        await service.set_fan_mode(QolsysFanMode.FAN_HIGH)
        device.controller.commands.zwave.thermostat_fan_mode_set.assert_awaited_once_with("8", "0", ThermostatFanMode.HIGH)

    @pytest.mark.asyncio
    async def test_set_fan_mode_unsupported_does_not_send(self) -> None:
        # FAN_OFF has no Z-Wave mapping -> should log and send nothing.
        service, device = _make()
        await service.set_fan_mode(QolsysFanMode.FAN_OFF)
        device.controller.commands.zwave.thermostat_fan_mode_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_set_temperature_cool(self) -> None:
        service, device = _make()
        service._hvac_modes = [QolsysHvacMode.COOL, QolsysHvacMode.HEAT]
        await service.set_temperature(72.0, QolsysHvacMode.COOL)
        device.controller.commands.zwave.thermostat_setpoint_set.assert_awaited_once_with(
            "8", "0", ThermostatSetpointMode.COOLING, 72
        )

    @pytest.mark.asyncio
    async def test_set_temperature_heat_truncates_to_int(self) -> None:
        service, device = _make()
        service._hvac_modes = [QolsysHvacMode.HEAT]
        await service.set_temperature(68.9, QolsysHvacMode.HEAT)
        device.controller.commands.zwave.thermostat_setpoint_set.assert_awaited_once_with(
            "8", "0", ThermostatSetpointMode.HEATING, 68
        )

    @pytest.mark.asyncio
    async def test_set_temperature_rejects_non_heat_cool_mode(self) -> None:
        service, device = _make()
        service._hvac_modes = [QolsysHvacMode.AUTO]
        await service.set_temperature(70.0, QolsysHvacMode.AUTO)
        device.controller.commands.zwave.thermostat_setpoint_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_set_temperature_rejects_mode_not_supported_by_device(self) -> None:
        # COOL is a valid setpoint mode, but the device does not list it in hvac_modes.
        service, device = _make()
        service._hvac_modes = []
        await service.set_temperature(70.0, QolsysHvacMode.COOL)
        device.controller.commands.zwave.thermostat_setpoint_set.assert_not_awaited()

    def test_to_dict_event(self) -> None:
        service, _ = _make()
        service._hvac_mode = QolsysHvacMode.COOL
        result = service.to_dict_event()
        assert result["service_type"] == "ThermostatServiceZwave"
        assert result["state"]["hvac_mode"] == "COOL"
