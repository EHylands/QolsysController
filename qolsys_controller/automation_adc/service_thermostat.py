from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_thermostat import ThermostatService
from qolsys_controller.enum_adc import (
    ADC_TO_QOLSYS_FAN_MODE,
    ADC_TO_QOLSYS_THERMOSTAT_MODE,
    QOLSYS_TO_ADC_FAN_MODE,
    QOLSYS_TO_ADC_THERMOSTAT_MODE,
    AdcFanMode,
    AdcThermostatMode,
    vdFuncLocalControl,
    vdFuncName,
    vdFuncType,
)
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysNotification, QolsysTemperatureUnit
from qolsys_controller.observable import Event

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class ThermostatServiceADC(ThermostatService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "ThermostatServiceADC"
        self._func_type: vdFuncType = vdFuncType.THERMOSTAT_MODE

        # Set defautl hvac_modes
        self.hvac_modes = [QolsysHvacMode.OFF, QolsysHvacMode.COOL, QolsysHvacMode.HEAT, QolsysHvacMode.HEAT_COOL]
        self.fan_modes = [QolsysFanMode.FAN_ON, QolsysFanMode.FAN_AUTO]

        self.is_main_endpoint_service = True

        self._min_heat_setpoint = 0.0
        self._max_heat_setpoint = 0.0
        self._min_cool_setpoint = 0.0
        self._max_cool_setpoint = 0.0

    @property
    def func_type(self) -> vdFuncType:
        return self._func_type

    def update_adc_service(
        self,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: int,
        timestamp: str,
    ) -> None:
        # ThermostatServiceADC only containt thermostat mode
        # Have to read other values from ADC Device to populate ThermostatServiceADC
        # (temperature, humidity, fan mode, setpoints, etc)
        # Imported lazily to avoid a circular import at module load time
        # (automation.device -> automation_adc.thermostat_service -> automation_adc.device).
        from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC

        if not isinstance(self.automation_device, QolsysAutomationDeviceADC):
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - update_adc_service - automation_device is not QolsysAutomationDeviceADC",
                self.automation_device.prefix,
                self.endpoint,
            )
            return

        try:
            json_func_list = json.loads(self.automation_device.func_list)

            # First thing to do is to set device temperature unit:
            for function in json_func_list:
                func_type = vdFuncType(function.get("vdFuncType"))
                func_state = function.get("vdFuncState")

                if func_type == vdFuncType.TEMPERATURE_UNITS:
                    current_unit = QolsysTemperatureUnit.CELSIUS
                    if func_state == 0:
                        current_unit = QolsysTemperatureUnit.FAHRENHEIT
                        self.device_temperature_unit = current_unit

            # Set other properties afterward
            for function in json_func_list:
                func_type = vdFuncType(function.get("vdFuncType"))
                func_state = function.get("vdFuncState")

                if func_type == vdFuncType.TEMPERATURE:
                    try:
                        self.current_temperature = int(func_state) / 10
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - TEMPERATURE func_state is not an int: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.FAN_MODE:
                    LOGGER.debug(
                        "%s[%s] ThermostatServiceADC - adc fan mode: %r",
                        self.automation_device.prefix,
                        self.endpoint,
                        func_state,
                    )

                    try:
                        adc_fan_mode = AdcFanMode(func_state)
                        self.fan_mode = ADC_TO_QOLSYS_FAN_MODE.get(adc_fan_mode, None)
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - FAN_MODE func_state is invalid: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.SUPPORTED_THERMOSTAT_MODES:
                    LOGGER.debug(
                        "%s[%s] ThermostatServiceADC - adc thermostat modes: %r",
                        self.automation_device.prefix,
                        self.endpoint,
                        func_state,
                    )

                elif func_type == vdFuncType.THERMOSTAT_MODE:
                    LOGGER.debug(
                        "%s[%s] ThermostatServiceADC - adc thermostat mode: %r",
                        self.automation_device.prefix,
                        self.endpoint,
                        func_state,
                    )

                    try:
                        adc_thermostat_mode = AdcThermostatMode(func_state)
                        self.hvac_mode = ADC_TO_QOLSYS_THERMOSTAT_MODE.get(adc_thermostat_mode, None)
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - HUMIDITY func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.HUMIDITY:
                    try:
                        self.current_humidity = int(func_state)
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - HUMIDITY func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.COOL_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self.target_cool_temp = temp
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - COOL_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.HEAT_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self.target_heat_temp = temp
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - HEAT_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.MAX_COOL_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self._max_cool_setpoint = temp
                            self.automation_device.notify(
                                Event(
                                    QolsysNotification.AUTOMATION_UPDATE,
                                    self.automation_device,
                                    self.automation_device.to_dict_event(),
                                )
                            )
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - MAX_COOL_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.MIN_COOL_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self._min_cool_setpoint = temp
                            self.automation_device.notify(
                                Event(
                                    QolsysNotification.AUTOMATION_UPDATE,
                                    self.automation_device,
                                    self.automation_device.to_dict_event(),
                                )
                            )
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - MIN_COOL_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.MAX_HEAT_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self._max_heat_setpoint = temp
                            self.automation_device.notify(
                                Event(
                                    QolsysNotification.AUTOMATION_UPDATE,
                                    self.automation_device,
                                    self.automation_device.to_dict_event(),
                                )
                            )
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - MAX_HEAT_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.MIN_HEAT_SETPOINT:
                    try:
                        temp = int(func_state) / 10
                        if temp >= 0:
                            self._min_heat_setpoint = temp
                            self.automation_device.notify(
                                Event(
                                    QolsysNotification.AUTOMATION_UPDATE,
                                    self.automation_device,
                                    self.automation_device.to_dict_event(),
                                )
                            )
                    except (TypeError, ValueError):
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - MIN_HEAT_SETPOINT func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

        except json.JSONDecodeError as e:
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - update_adc_service - error decoding func_list: %s",
                self.automation_device.prefix,
                self.endpoint,
                e,
            )
            return

    async def turn_on(self) -> None:
        pass

    async def turn_off(self) -> None:
        LOGGER.debug("%s[%s] ThermostatServiceADC - turn off", self.automation_device.prefix, self.endpoint)
        await self.automation_device.controller.commands.adc.virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, AdcThermostatMode.OFF
        )

    async def set_temperature(self, temperature: float, mode: QolsysHvacMode) -> None:

        if mode not in (QolsysHvacMode.HEAT, QolsysHvacMode.COOL):
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - set_temperature - unsupported hvac_mode: %s",
                self.automation_device.prefix,
                self.endpoint,
                mode,
            )
            return

        if mode not in self.hvac_modes:
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - set_temperature - hvac_mode not supported by device: %s",
                self.automation_device.prefix,
                self.endpoint,
                mode,
            )
            return

        if mode == QolsysHvacMode.HEAT:
            if temperature < self._min_heat_setpoint or temperature > self._max_heat_setpoint:
                LOGGER.error(
                    "%s[%s] ThermostatServiceADC - set_temperature - heat temperature out of range: %s",
                    self.automation_device.prefix,
                    self.endpoint,
                    temperature,
                )
                return

            vd_func_id = self._get_func_name_id(vdFuncName.HEAT_SETPOINT)
            if vd_func_id == -1:
                LOGGER.error(
                    "%s[%s] ThermostatServiceADC - set_temperature - could not find HEAT_SETPOINT function ID",
                    self.automation_device.prefix,
                    self.endpoint,
                )
                return

            await self.automation_device.controller.commands.adc.virtual_device_action(
                self.automation_device.virtual_node_id, vd_func_id, int(temperature * 10)
            )
        elif mode == QolsysHvacMode.COOL:
            if temperature < self._min_cool_setpoint or temperature > self._max_cool_setpoint:
                LOGGER.error(
                    "%s[%s] ThermostatServiceADC - set_temperature - cool temperature out of range: %s",
                    self.automation_device.prefix,
                    self.endpoint,
                    temperature,
                )
                return

            vd_func_id = self._get_func_name_id(vdFuncName.COOL_SETPOINT)
            if vd_func_id == -1:
                LOGGER.error(
                    "%s[%s] ThermostatServiceADC - set_temperature - could not find COOL_SETPOINT function ID",
                    self.automation_device.prefix,
                    self.endpoint,
                )
                return

            await self.automation_device.controller.commands.adc.virtual_device_action(
                self.automation_device.virtual_node_id, vd_func_id, int(temperature * 10)
            )

    async def set_hvac_mode(self, hvac_mode: QolsysHvacMode) -> None:
        adc_thermostat_mode = QOLSYS_TO_ADC_THERMOSTAT_MODE.get(hvac_mode, None)
        if adc_thermostat_mode:
            await self.automation_device.controller.commands.adc.virtual_device_action(
                self.automation_device.virtual_node_id, self.endpoint, adc_thermostat_mode
            )

    async def set_fan_mode(self, fan_mode: QolsysFanMode) -> None:
        adc_fan_mode = QOLSYS_TO_ADC_FAN_MODE.get(fan_mode, None)
        if adc_fan_mode:
            await self.automation_device.controller.commands.adc.virtual_device_action(
                self.automation_device.virtual_node_id, self.endpoint, adc_fan_mode
            )

    async def set_humidity(self, humidity: float) -> None:
        pass

    def update_automation_service(self) -> None:
        pass

    @property
    def min_temp(self) -> float:
        match self.hvac_mode:
            case QolsysHvacMode.HEAT:
                return self._min_heat_setpoint

            case QolsysHvacMode.COOL:
                return self._min_cool_setpoint

            case QolsysHvacMode.HEAT_COOL:
                return min(self._min_heat_setpoint, self._min_cool_setpoint)

            case QolsysHvacMode.OFF:
                return min(self._min_heat_setpoint, self._min_cool_setpoint)

        return -1.0

    @property
    def max_temp(self) -> float:
        match self.hvac_mode:
            case QolsysHvacMode.HEAT:
                return self._max_heat_setpoint

            case QolsysHvacMode.COOL:
                return self._max_cool_setpoint

            case QolsysHvacMode.HEAT_COOL:
                return max(self._max_heat_setpoint, self._max_cool_setpoint)

            case QolsysHvacMode.OFF:
                return max(self._max_heat_setpoint, self._max_cool_setpoint)

        return -1.0

    def _get_func_name_id(self, func_name: vdFuncName) -> int:
        # Imported lazily to avoid a circular import at module load time
        # (automation.device -> automation_adc.thermostat_service -> automation_adc.device).
        from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC

        func_id = -1

        if not isinstance(self.automation_device, QolsysAutomationDeviceADC):
            return func_id

        try:
            json_func_list = json.loads(self.automation_device.func_list)
            for function in json_func_list:
                if vdFuncName(function.get("vdFuncName")) == func_name:
                    func_id = function.get("vdFuncId")
                    break

        except json.JSONDecodeError as e:
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - _get_func_name_id - error decoding func_list: %s",
                self.automation_device.prefix,
                self.endpoint,
                e,
            )

        except ValueError as e:
            LOGGER.error(
                "%s[%s] ThermostatServiceADC - _get_func_name_id - error parsing func_list: %s",
                self.automation_device.prefix,
                self.endpoint,
                e,
            )
        return func_id
