"""Tests for ThermostatServiceADC decoding a real ADC thermostat func_list."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC
from qolsys_controller.automation_adc.service_thermostat import ThermostatServiceADC
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysTemperatureUnit

# Real func_list captured from an ADC thermostat, stored verbatim as the JSON
# string the panel delivers. Values are encoded as ints under "vdFuncState"
# (temperature is deci-degrees, i.e. 806 -> 80.6).
FUNC_LIST = '[{"vdFuncId":1,"vdFuncName":"Local Temperature","vdFuncLocalControl":1,"vdFuncType":4,"vdFuncState":806,"vdFuncBackendTimestamp":1790462621523},{"vdFuncId":2,"vdFuncName":"Malfunction","vdFuncType":10,"vdFuncLocalControl":1,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":3,"vdFuncName":"Humidity In Percentage","vdFuncLocalControl":1,"vdFuncType":20,"vdFuncState":57,"vdFuncBackendTimestamp":1790462621523},{"vdFuncId":4,"vdFuncName":"Heat Setpoint","vdFuncLocalControl":2,"vdFuncType":21,"vdFuncState":-4000,"vdFuncBackendTimestamp":1790396235353},{"vdFuncId":5,"vdFuncName":"Min Heat Setpoint Limit","vdFuncType":22,"vdFuncLocalControl":1,"vdFuncState":450,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":6,"vdFuncName":"Max Heat Setpoint Limit","vdFuncType":23,"vdFuncLocalControl":1,"vdFuncState":790,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":7,"vdFuncName":"Cool Setpoint","vdFuncType":24,"vdFuncLocalControl":2,"vdFuncState":800,"vdFuncBackendTimestamp":1790396235353},{"vdFuncId":8,"vdFuncName":"Min Cool Setpoint Limit","vdFuncType":25,"vdFuncLocalControl":1,"vdFuncState":650,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":9,"vdFuncName":"Max Cool Setpoint Limit","vdFuncLocalControl":1,"vdFuncType":26,"vdFuncState":920,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":10,"vdFuncName":"Thermostat System Mode","vdFuncLocalControl":2,"vdFuncType":27,"vdFuncState":1,"vdFuncBackendTimestamp":1784073405779},{"vdFuncId":11,"vdFuncName":"Fan Mode","vdFuncLocalControl":2,"vdFuncType":28,"vdFuncState":5,"vdFuncBackendTimestamp":1783391961539},{"vdFuncId":12,"vdFuncName":"Temperature Units","vdFuncLocalControl":1,"vdFuncType":29,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343},{"vdFuncId":13,"vdFuncName":"Thermostat System Modes Supported","vdFuncLocalControl":1,"vdFuncType":30,"vdFuncState":0,"vdFuncBackendTimestamp":1781277665343}]'  # noqa: E501


def _make_device() -> QolsysAutomationDeviceADC:
    return QolsysAutomationDeviceADC(
        controller=MagicMock(),
        adc_dict={"_id": "1", "device_id": "42", "name": "Living Room Thermostat", "func_list": FUNC_LIST},
    )


def _get_thermostat(dev: QolsysAutomationDeviceADC) -> ThermostatServiceADC:
    for services in dev.services.values():
        for service in services:
            if isinstance(service, ThermostatServiceADC):
                return service
    raise AssertionError("No ThermostatServiceADC was created")


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
