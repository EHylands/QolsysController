"""Tests for ThermostatServiceZwave command dispatch."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_zwave.service_thermostat import ThermostatServiceZwave
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacAction, QolsysHvacMode
from qolsys_controller.enum_zwave import (
    ThermostatFanMode,
    ThermostatMode,
    ThermostatOperatingState,
    ThermostatSetpointMode,
)


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
    async def test_set_temperature_heat_rounds_to_nearest_int(self) -> None:
        service, device = _make()
        service._hvac_modes = [QolsysHvacMode.HEAT]
        await service.set_temperature(68.9, QolsysHvacMode.HEAT)
        device.controller.commands.zwave.thermostat_setpoint_set.assert_awaited_once_with(
            "8", "0", ThermostatSetpointMode.HEATING, 69
        )

    @pytest.mark.asyncio
    async def test_set_temperature_heat_rounds_down(self) -> None:
        service, device = _make()
        service._hvac_modes = [QolsysHvacMode.HEAT]
        await service.set_temperature(68.4, QolsysHvacMode.HEAT)
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

    def test_reported_hvac_action_overrides_inferred(self) -> None:
        # With HEAT mode and current < target, the inferred action would be HEATING;
        # a device-reported operating state must take precedence.
        service, _ = _make()
        service._hvac_mode = QolsysHvacMode.HEAT
        service._current_temperature = 60.0
        service._target_heat_temp = 70.0
        assert service.hvac_action == QolsysHvacAction.HEATING  # inferred fallback

        service.hvac_action = QolsysHvacAction.IDLE
        assert service.hvac_action == QolsysHvacAction.IDLE
        assert service.to_dict_event()["state"]["hvac_action"] == "IDLE"

    def test_hvac_action_setter_notifies_once_per_change(self) -> None:
        service, device = _make()
        device.notify.reset_mock()

        service.hvac_action = QolsysHvacAction.COOLING
        service.hvac_action = QolsysHvacAction.COOLING  # unchanged -> no extra notify
        assert device.notify.call_count == 1

    def test_operating_state_mapping_is_complete(self) -> None:
        # Every Z-Wave operating state must map to a QolsysHvacAction.
        mapping = ThermostatServiceZwave.ZWAVE_OPERATING_STATE_TO_QOLSYS_HVAC_ACTION
        for state in ThermostatOperatingState:
            assert mapping[state] is not None

    def test_operating_state_mapping_values(self) -> None:
        mapping = ThermostatServiceZwave.ZWAVE_OPERATING_STATE_TO_QOLSYS_HVAC_ACTION
        assert mapping[ThermostatOperatingState.IDLE] == QolsysHvacAction.IDLE
        assert mapping[ThermostatOperatingState.HEATING] == QolsysHvacAction.HEATING
        assert mapping[ThermostatOperatingState.COOLING] == QolsysHvacAction.COOLING
        assert mapping[ThermostatOperatingState.FAN_ONLY] == QolsysHvacAction.FAN
        assert mapping[ThermostatOperatingState.PENDING_HEAT] == QolsysHvacAction.PREHEATING
        assert mapping[ThermostatOperatingState.PENDING_COOL] == QolsysHvacAction.IDLE
        assert mapping[ThermostatOperatingState.VENT_ECONOMIZER] == QolsysHvacAction.FAN
        assert mapping[ThermostatOperatingState.AUXILIARY_HEATING] == QolsysHvacAction.HEATING
        assert mapping[ThermostatOperatingState.SECOND_STAGE_HEATING] == QolsysHvacAction.HEATING
        assert mapping[ThermostatOperatingState.SECOND_STAGE_COOLING] == QolsysHvacAction.COOLING
        assert mapping[ThermostatOperatingState.SECOND_STAGE_AUXILIARY_HEATING] == QolsysHvacAction.HEATING
        assert mapping[ThermostatOperatingState.THIRD_STAGE_HEATING] == QolsysHvacAction.HEATING
