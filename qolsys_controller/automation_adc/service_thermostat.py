from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_thermostat import ThermostatService
from qolsys_controller.enum_adc import (
    ADCT_TO_QOLSYS_THERMOSTAT_MODE,
    QOLSYS_TO_ADC_THERMOSTAT_MODE,
    AdcThermostatMode,
    vdFuncLocalControl,
    vdFuncName,
    vdFuncType,
)
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysTemperatureUnit

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class ThermostatServiceADC(ThermostatService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "ThermostatServiceADC"
        # Outbound actions (set_hvac_mode / turn_off) send a thermostat mode change
        self._func_type: vdFuncType = vdFuncType.THERMOSTAT_MODE
        self.is_main_endpoint_service = True

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
                    except TypeError, ValueError:
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
                        self.hvac_mode = ADCT_TO_QOLSYS_THERMOSTAT_MODE.get(adc_thermostat_mode, None)
                    except TypeError, ValueError:
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - HUMIDITY func_state is not a number: %r",
                            self.automation_device.prefix,
                            self.endpoint,
                            func_state,
                        )

                elif func_type == vdFuncType.HUMIDITY:
                    try:
                        self.current_humidity = float(func_state)
                    except TypeError, ValueError:
                        LOGGER.error(
                            "%s[%s] ThermostatServiceADC - HUMIDITY func_state is not a number: %r",
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
        await self.automation_device.controller.commands.adc.virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, AdcThermostatMode.OFF
        )

    async def set_temperature(self, temperature: float, mode: QolsysHvacMode) -> None:
        pass
        if mode not in (QolsysHvacMode.HEAT, QolsysHvacMode.COOL):
            LOGGER.error(
                "%s[%s] ThermostatServiceZwave - set_temperature - unsupported hvac_mode: %s",
                self.automation_device.prefix,
                self.endpoint,
                mode,
            )
            return

        if mode not in self.hvac_modes:
            LOGGER.error(
                "%s[%s] ThermostatServiceZwave - set_temperature - hvac_mode not supported by device: %s",
                self.automation_device.prefix,
                self.endpoint,
                mode,
            )
            return

    async def set_hvac_mode(self, hvac_mode: QolsysHvacMode) -> None:
        adc_thermostat_mode = QOLSYS_TO_ADC_THERMOSTAT_MODE.get(hvac_mode, None)
        if adc_thermostat_mode:
            await self.automation_device.controller.commands.adc.virtual_device_action(
                self.automation_device.virtual_node_id, self.endpoint, adc_thermostat_mode
            )

    async def set_fan_mode(self, fan_mode: QolsysFanMode) -> None:
        pass

    async def set_humidity(self, humidity: float) -> None:
        pass

    def update_automation_service(self) -> None:
        pass
