from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_thermostat import ThermostatService
from qolsys_controller.enum_qolsys import QolsysFanMode, QolsysHvacMode, QolsysPanelType
from qolsys_controller.enum_zwave import ThermostatMode, ThermostatSetpointMode

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class ThermostatServiceZwave(ThermostatService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "ThermostatServiceZwave"

    async def turn_on(self) -> None:
        pass

    async def turn_off(self) -> None:
        await self.automation_device.controller.commands.zwave.thermostat_mode_set(
            self.automation_device.virtual_node_id, str(self.endpoint), ThermostatMode.OFF
        )

    async def set_temperature(self, temperature: float, mode: QolsysHvacMode) -> None:
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

        setpoint_mode: ThermostatSetpointMode = ThermostatSetpointMode.HEATING
        if mode == QolsysHvacMode.COOL:
            setpoint_mode = ThermostatSetpointMode.COOLING

        await self.automation_device.controller.commands.zwave.thermostat_setpoint_set(
            self.automation_device.virtual_node_id, str(self.endpoint), setpoint_mode, int(temperature)
        )

        # Ask for report on IQ2+ panel
        if self.automation_device.controller.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            # Set the value preemptively
            if mode == QolsysHvacMode.COOL:
                self.target_cool_temp = temperature
            elif mode == QolsysHvacMode.HEAT:
                self.target_heat_temp = temperature

            await self.automation_device.controller.commands.zwave.thermostat_setpoint_get(
                self.automation_device.virtual_node_id, str(self.endpoint), setpoint_mode
            )

    async def set_hvac_mode(self, hvac_mode: QolsysHvacMode) -> None:
        zwave_thermostat_mode = self.QOLSYS_TO_ZWAVE_HVAC_MODE.get(hvac_mode, None)
        if zwave_thermostat_mode is None:
            LOGGER.error(
                "%s[%s] ThermostatServiceZwave - set_hvac_mode - unsupported hvac_mode: %s",
                self.automation_device.prefix,
                self.endpoint,
                hvac_mode,
            )
            return

        await self.automation_device.controller.commands.zwave.thermostat_mode_set(
            self.automation_device.virtual_node_id, str(self.endpoint), zwave_thermostat_mode
        )

        # Ask for report on IQ2+ panel
        if self.automation_device.controller.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            # Set the value preemptively
            self.hvac_mode = hvac_mode

            await self.automation_device.controller.commands.zwave.thermostat_mode_get(
                self.automation_device.virtual_node_id, str(self.endpoint)
            )

    async def set_fan_mode(self, fan_mode: QolsysFanMode) -> None:
        zwave_fan_mode = self.QOLSYS_TO_ZWAVE_FAN_MODE.get(fan_mode, None)
        if zwave_fan_mode is None:
            LOGGER.error(
                "%s[%s] ThermostatServiceZwave - set_fan_mode - unsupported fan_mode: %s",
                self.automation_device.prefix,
                self.endpoint,
                fan_mode,
            )
            return
        await self.automation_device.controller.commands.zwave.thermostat_fan_mode_set(
            self.automation_device.virtual_node_id, str(self.endpoint), zwave_fan_mode
        )

        # Ask for report on IQ2+ panel
        if self.automation_device.controller.panel.product_type == QolsysPanelType.IQ_PANEL_2_PLUS:
            # Set the value preemptively
            self.fan_mode = fan_mode

            await self.automation_device.controller.commands.zwave.thermostat_fan_mode_get(
                self.automation_device.virtual_node_id, str(self.endpoint)
            )

    async def set_humidity(self, humidity: float) -> None:
        pass

    def update_automation_service(self) -> None:
        super().update_automation_service()
