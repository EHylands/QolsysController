"""Tests for ThermostatServiceADC decoding a real ADC thermostat func_list."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC
from qolsys_controller.automation_adc.service_thermostat import ThermostatServiceADC
from qolsys_controller.enum_adc import AdcFanMode, AdcThermostatMode
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysTemperatureUnit

# Real func_list captured from an ADC thermostat, stored verbatim as the JSON
# string the panel delivers. Values are encoded as ints under "vdFuncState"
# (temperature is deci-degrees, i.e. 806 -> 80.6).
FUNC_LIST = '[{"vdFuncId":1,"vdFuncName":"Local Temperature","vdFuncLocalControl":1,"vdFuncType":4,"vdFuncState":806,"vdFuncBackendTimestamp":1790462621523},{"vdFuncId":2,"vdFuncName":"Malfunction","vdFuncType":10,"vdFuncLocalControl":1,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":3,"vdFuncName":"Humidity In Percentage","vdFuncLocalControl":1,"vdFuncType":20,"vdFuncState":57,"vdFuncBackendTimestamp":1790462621523},{"vdFuncId":4,"vdFuncName":"Heat Setpoint","vdFuncLocalControl":2,"vdFuncType":21,"vdFuncState":-4000,"vdFuncBackendTimestamp":1790396235353},{"vdFuncId":5,"vdFuncName":"Min Heat Setpoint Limit","vdFuncType":22,"vdFuncLocalControl":1,"vdFuncState":450,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":6,"vdFuncName":"Max Heat Setpoint Limit","vdFuncType":23,"vdFuncLocalControl":1,"vdFuncState":790,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":7,"vdFuncName":"Cool Setpoint","vdFuncType":24,"vdFuncLocalControl":2,"vdFuncState":800,"vdFuncBackendTimestamp":1790396235353},{"vdFuncId":8,"vdFuncName":"Min Cool Setpoint Limit","vdFuncType":25,"vdFuncLocalControl":1,"vdFuncState":650,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":9,"vdFuncName":"Max Cool Setpoint Limit","vdFuncLocalControl":1,"vdFuncType":26,"vdFuncState":920,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":10,"vdFuncName":"Thermostat System Mode","vdFuncLocalControl":2,"vdFuncType":27,"vdFuncState":1,"vdFuncBackendTimestamp":1784073405779},{"vdFuncId":11,"vdFuncName":"Fan Mode","vdFuncLocalControl":2,"vdFuncType":28,"vdFuncState":5,"vdFuncBackendTimestamp":1783391961539},{"vdFuncId":12,"vdFuncName":"Temperature Units","vdFuncLocalControl":1,"vdFuncType":29,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":13,"vdFuncName":"Thermostat System Modes Supported","vdFuncLocalControl":1,"vdFuncType":30,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343}]'  # noqa: E501


# Variant with the Heat/Cool Setpoint entries removed but the Min/Max limit
# entries kept, so the range check passes yet _get_func_name_id returns -1.
FUNC_LIST_NO_SETPOINTS = (
    "["
    '{"vdFuncId":5,"vdFuncName":"Min Heat Setpoint Limit","vdFuncType":22,"vdFuncLocalControl":1,"vdFuncState":450},'
    '{"vdFuncId":6,"vdFuncName":"Max Heat Setpoint Limit","vdFuncType":23,"vdFuncLocalControl":1,"vdFuncState":790},'
    '{"vdFuncId":8,"vdFuncName":"Min Cool Setpoint Limit","vdFuncType":25,"vdFuncLocalControl":1,"vdFuncState":650},'
    '{"vdFuncId":9,"vdFuncName":"Max Cool Setpoint Limit","vdFuncType":26,"vdFuncLocalControl":1,"vdFuncState":920},'
    '{"vdFuncId":10,"vdFuncName":"Thermostat System Mode","vdFuncType":27,"vdFuncLocalControl":2,"vdFuncState":1},'
    '{"vdFuncId":12,"vdFuncName":"Temperature Units","vdFuncType":29,"vdFuncLocalControl":1,"vdFuncState":0}'
    "]"
)


def _make_device(func_list: str = FUNC_LIST) -> QolsysAutomationDeviceADC:
    return QolsysAutomationDeviceADC(
        controller=MagicMock(),
        adc_dict={"_id": "1", "device_id": "42", "name": "Living Room Thermostat", "func_list": func_list},
    )


def _get_thermostat(dev: QolsysAutomationDeviceADC) -> ThermostatServiceADC:
    for services in dev.services.values():
        for service in services:
            if isinstance(service, ThermostatServiceADC):
                return service
    raise AssertionError("No ThermostatServiceADC was created")


def _install_action(dev: QolsysAutomationDeviceADC) -> AsyncMock:
    """Replace the awaitable panel command with an AsyncMock we can assert on.

    ``dev.controller`` is a MagicMock at runtime (see ``_make_device``); the
    ignore silences mypy flagging assignment to the real controller's method.
    """
    action = AsyncMock()
    dev.controller.commands.adc.virtual_device_action = action  # type: ignore[method-assign]
    return action


class TestThermostatServiceADC:
    def test_func_list_does_not_crash_construction(self) -> None:
        # Regression: decoding read the wrong JSON key ("func_state" instead of
        # "vdFuncState"), so every value was None and float(None) crashed the
        # whole device __init__.
        _make_device()

    def test_thermostat_service_created(self) -> None:
        assert _get_thermostat(_make_device()) is not None

    def test_temperature_decoded(self) -> None:
        # vdFuncState 806 is deci-degrees -> 80.6
        assert _get_thermostat(_make_device()).current_temperature == 80.6

    def test_humidity_decoded(self) -> None:
        assert _get_thermostat(_make_device()).current_humidity == 57.0

    def test_hvac_mode_decoded(self) -> None:
        # vdFuncState 1 -> HEAT_COOL (AdcThermostatMode.HEAT_COOL == 1)
        assert _get_thermostat(_make_device()).hvac_mode == QolsysHvacMode.HEAT_COOL

    def test_temperature_unit_decoded(self) -> None:
        # Temperature Units vdFuncState 0 -> Fahrenheit
        assert _get_thermostat(_make_device()).device_temperature_unit == QolsysTemperatureUnit.FAHRENHEIT

    def test_fan_mode_decoded(self) -> None:
        # Fan Mode vdFuncState 5 -> AdcFanMode.AUTO -> QolsysFanMode.FAN_AUTO
        assert _get_thermostat(_make_device()).fan_mode == QolsysFanMode.FAN_AUTO

    def test_cool_setpoint_decoded(self) -> None:
        # Cool Setpoint vdFuncState 800 is deci-degrees -> 80.0
        assert _get_thermostat(_make_device()).target_cool_temp == 80.0

    def test_negative_heat_setpoint_ignored(self) -> None:
        # Heat Setpoint vdFuncState -4000 is a negative sentinel ("not set"):
        # the >= 0 guard must drop it rather than report -400.0.
        assert _get_thermostat(_make_device()).target_heat_temp is None

    def test_setpoint_limits_decoded(self) -> None:
        ts = _get_thermostat(_make_device())
        # Deci-degrees -> degrees for each Min/Max Heat/Cool Setpoint Limit.
        assert ts._min_heat_setpoint == 45.0
        assert ts._max_heat_setpoint == 79.0
        assert ts._min_cool_setpoint == 65.0
        assert ts._max_cool_setpoint == 92.0

    def test_min_max_temp_properties_in_heat_cool(self) -> None:
        # System Mode is HEAT_COOL -> min/max span both heat and cool limits.
        ts = _get_thermostat(_make_device())
        assert ts.min_temp == 45.0
        assert ts.max_temp == 92.0


class TestThermostatServiceADCSetTemperature:
    async def test_heat_sends_heat_setpoint(self) -> None:
        # HEAT within [45.0, 79.0] -> command carries the Heat Setpoint's
        # vdFuncId (4) and the temperature as deci-degrees (72.0 -> 720).
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(72.0, QolsysHvacMode.HEAT)
        action.assert_awaited_once_with("42", 4, 720)

    async def test_cool_sends_cool_setpoint(self) -> None:
        # COOL within [65.0, 92.0] -> Cool Setpoint vdFuncId (7), 75.0 -> 750.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(75.0, QolsysHvacMode.COOL)
        action.assert_awaited_once_with("42", 7, 750)

    async def test_heat_setpoint_boundaries_allowed(self) -> None:
        # The range check is inclusive: exact min/max must be sent, not rejected.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(45.0, QolsysHvacMode.HEAT)
        await _get_thermostat(dev).set_temperature(79.0, QolsysHvacMode.HEAT)
        assert action.await_args_list[0].args == ("42", 4, 450)
        assert action.await_args_list[1].args == ("42", 4, 790)

    async def test_heat_above_range_rejected(self) -> None:
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(200.0, QolsysHvacMode.HEAT)
        action.assert_not_awaited()

    async def test_heat_below_range_rejected(self) -> None:
        # 40.0 is below the 45.0 min heat setpoint limit.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(40.0, QolsysHvacMode.HEAT)
        action.assert_not_awaited()

    async def test_cool_above_range_rejected(self) -> None:
        # 100.0 is above the 92.0 max cool setpoint limit.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(100.0, QolsysHvacMode.COOL)
        action.assert_not_awaited()

    async def test_unsupported_mode_rejected(self) -> None:
        # Only HEAT/COOL target a single setpoint; HEAT_COOL and OFF are refused.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(72.0, QolsysHvacMode.HEAT_COOL)
        await _get_thermostat(dev).set_temperature(72.0, QolsysHvacMode.OFF)
        action.assert_not_awaited()

    async def test_mode_not_in_device_hvac_modes_rejected(self) -> None:
        # Second guard: even a HEAT/COOL request is refused when the device
        # does not advertise that mode.
        dev = _make_device()
        action = _install_action(dev)
        ts = _get_thermostat(dev)
        ts.hvac_modes = [QolsysHvacMode.COOL]
        await ts.set_temperature(72.0, QolsysHvacMode.HEAT)
        action.assert_not_awaited()

    async def test_heat_missing_setpoint_id_rejected(self) -> None:
        # In-range request but no Heat Setpoint entry in func_list -> the
        # function-ID guard must bail rather than send service_id -1.
        dev = _make_device(FUNC_LIST_NO_SETPOINTS)
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(72.0, QolsysHvacMode.HEAT)
        action.assert_not_awaited()

    async def test_cool_missing_setpoint_id_rejected(self) -> None:
        dev = _make_device(FUNC_LIST_NO_SETPOINTS)
        action = _install_action(dev)
        await _get_thermostat(dev).set_temperature(75.0, QolsysHvacMode.COOL)
        action.assert_not_awaited()


class TestThermostatServiceADCSetMode:
    async def test_set_hvac_mode_targets_system_mode_func(self) -> None:
        # Thermostat System Mode is vdFuncId 10; COOL -> AdcThermostatMode.COOL.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_hvac_mode(QolsysHvacMode.COOL)
        action.assert_awaited_once_with("42", 10, AdcThermostatMode.COOL)

    async def test_set_hvac_mode_off_is_sent(self) -> None:
        # Regression: AdcThermostatMode.OFF == 0, so a truthiness guard would
        # have silently skipped the command.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_hvac_mode(QolsysHvacMode.OFF)
        action.assert_awaited_once_with("42", 10, AdcThermostatMode.OFF)

    async def test_set_fan_mode_targets_fan_func(self) -> None:
        # Fan Mode is vdFuncId 11 (not the service endpoint 10); AUTO -> 5.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_fan_mode(QolsysFanMode.FAN_AUTO)
        action.assert_awaited_once_with("42", 11, AdcFanMode.AUTO)

    async def test_set_fan_mode_on_is_sent(self) -> None:
        # Regression: AdcFanMode.ON == 0 would be dropped by a truthiness guard.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_fan_mode(QolsysFanMode.FAN_ON)
        action.assert_awaited_once_with("42", 11, AdcFanMode.ON)

    async def test_set_fan_mode_unmapped_mode_rejected(self) -> None:
        # FAN_LOW has no ADC equivalent -> nothing is sent.
        dev = _make_device()
        action = _install_action(dev)
        await _get_thermostat(dev).set_fan_mode(QolsysFanMode.FAN_LOW)
        action.assert_not_awaited()

    async def test_set_fan_mode_missing_func_id_rejected(self) -> None:
        # func_list without a Fan Mode entry -> func-ID guard bails.
        dev = _make_device(FUNC_LIST_NO_SETPOINTS)
        action = _install_action(dev)
        await _get_thermostat(dev).set_fan_mode(QolsysFanMode.FAN_AUTO)
        action.assert_not_awaited()
