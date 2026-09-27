from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_thermostat import ThermostatService
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysTemperatureUnit

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice
    from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC

LOGGER = logging.getLogger(__name__)


class ThermostatServiceADC(ThermostatService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "ThermostatServiceADC"
        self._func_type: vdFuncType = vdFuncType.UNKNOWN
        self.is_main_endpoint_service = True

    def update_adc_service(
        self,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: vdFuncState,
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
                func_state = function.get("func_state")

                if func_type == vdFuncType.TEMPERATURE_UNITS:
                    current_unit = QolsysTemperatureUnit.CELSIUS
                    if func_state == 0:
                        current_unit = QolsysTemperatureUnit.FAHRENHEIT
                        self.device_temperature_unit = current_unit

            # Set other properties afterward
            for function in json_func_list:
                func_type = vdFuncType(function.get("vdFuncType"))
                func_state = function.get("func_state")

                if func_type == vdFuncType.TEMPERATURE:
                    self.current_temperature = int(func_state) / 10

                elif func_type == vdFuncType.THERMOSTAT_MODE:
                    current_thermostat_mode = QolsysHvacMode.OFF
                    if func_state == 1:
                        current_thermostat_mode == QolsysHvacMode.COOL
                    elif func_state == 2:
                        current_thermostat_mode = QolsysHvacMode.HEAT
                    elif func_state == 3:
                        current_thermostat_mode = QolsysHvacMode.HEAT_COOL

                    self.hvac_mode = current_thermostat_mode

                elif func_type == vdFuncType.HUMIDITY:
                    self.current_humidity = float(func_state)

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
        pass

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
        pass

    async def set_fan_mode(self, fan_mode: QolsysFanMode) -> None:
        pass

    async def set_humidity(self, humidity: float) -> None:
        pass

    def update_automation_service(self) -> None:
        pass
