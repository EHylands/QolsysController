from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.device import QolsysAutomationDevice
from qolsys_controller.automation.service_meter import MeterService
from qolsys_controller.automation.service_sensor import SensorService
from qolsys_controller.automation_zwave.service_central_scene import CentralSceneServiceZwave
from qolsys_controller.automation_zwave.service_light import LightServiceZwave
from qolsys_controller.automation_zwave.service_lock import LockServiceZwave
from qolsys_controller.automation_zwave.service_meter import MeterServiceZwave
from qolsys_controller.automation_zwave.service_outlet import OutletServiceZwave
from qolsys_controller.automation_zwave.service_sensor import SensorServiceZwave
from qolsys_controller.automation_zwave.service_siren import SirenServiceZwave
from qolsys_controller.automation_zwave.service_status import StatusServiceZwave
from qolsys_controller.automation_zwave.service_thermostat import ThermostatServiceZwave
from qolsys_controller.automation_zwave.service_valve import ValveServiceZwave
from qolsys_controller.enum_qolsys import AutomationDeviceProtocol, QolsysMeterType, map_to_qolsys_meter_scale
from qolsys_controller.enum_zwave import (
    CENTRAL_SCENE_EVENT_NAME,
    CentralSceneKeyAttribute,
    ZwaveCommandClass,
    ZwaveDeviceClass,
)
from qolsys_controller.mqtt_command import MQTTCommand_ZWave

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController


LOGGER = logging.getLogger(__name__)


class QolsysAutomationDeviceZwave(QolsysAutomationDevice):
    def __init__(self, controller: QolsysController, zwave_dict: dict[str, str], dict: dict[str, str]) -> None:
        super().__init__(controller, dict)

        # Base Z-Wave Device Properties
        self._id: str = zwave_dict.get("_id", "")
        self._node_id: str = zwave_dict.get("node_id", "")
        self._node_name: str = zwave_dict.get("node_name", "")
        self._node_type: str = zwave_dict.get("node_type", "")
        self._node_status: str = zwave_dict.get("node_status", "")
        self._partition_id: str = zwave_dict.get("partition_id", "")
        self._node_secure_cmd_cls: str = zwave_dict.get("node_secure_cmd_cls", "")
        self._node_battery_level: str = zwave_dict.get("node_battery_level", "")
        # self._node_battery_level_value: str = zwave_dict.get("node_battery_level_value", "")
        self._is_node_listening_node: str = zwave_dict.get("is_node_listening_node", "")
        self._basic_report_value: str = zwave_dict.get("basic_report_value", "")
        self._switch_multilevel_report_value: str = zwave_dict.get("switch_multilevel_report_value", "")
        self._basic_device_type: str = zwave_dict.get("basic_device_type", "")
        self._generic_device_type: str = zwave_dict.get("generic_device_type", "")
        self._specific_device_type: str = zwave_dict.get("specific_device_type", "")
        self._num_secure_command_class: str = zwave_dict.get("num_secure_command_class", "")
        self._secure_command_class: str = zwave_dict.get("secure_command_class", "")
        self._manufacture_id: str = zwave_dict.get("manufacture_id", "")
        self._product_type: str = zwave_dict.get("product_type", "")
        self._device_protocol: str = zwave_dict.get("device_protocol", "")
        self._paired_status: str = zwave_dict.get("paired_status", "")
        self._is_device_sleeping: str = zwave_dict.get("is_device_sleeping", "")
        self._is_device_hidden: str = zwave_dict.get("is_device_hidden", "")
        self._last_updated_date: str = zwave_dict.get("last_updated_date", "")
        self._meter_capabilities: str = ""
        self._multisensor_capabilities: str = ""

        self._notification_capabilities = zwave_dict.get("notification_capabilities", "")

        # Set protocol before running setters that add protocol-specific services
        self._protocol = AutomationDeviceProtocol.ZWAVE

        self._command_class_list: str = ""
        self.command_class_list = zwave_dict.get("command_class_list", "")

        self._multi_channel_details: str = ""
        self.multi_channel_details = zwave_dict.get("multi_channel_details", "")

        self._endpoint = zwave_dict.get("endpoint", "")
        self._endpoint_details = zwave_dict.get("endpoint_details", "")

        # Fix Meter multichannel endpoint
        self._FIX_MULTICHANNEL_METER_ENDPOINT: bool = False

        # Add Base Services
        endpoint = int(self.end_point) if self.end_point.isdigit() else 0
        self.service_add_status_service(endpoint=endpoint)
        self.service_add_battery_service(endpoint=endpoint)
        self.multisensor_capabilities: str = zwave_dict.get("multisensor_capabilities", "")
        self.meter_capabilities: str = zwave_dict.get("meter_capabilities", "")

        super().update_automation_services()

    def update_zwave_device(self, data: dict[str, str]) -> None:
        self.start_batch_update()

        if "multisensor_capabilities" in data:
            self.multisensor_capabilities = data.get("multisensor_capabilities", "")

        if "meter_capabilities" in data:
            self.meter_capabilities = data.get("meter_capabilities", "")

        if "node_status" in data:
            self.node_status = data.get("node_status", "")

        if "command_class_list" in data:
            self.command_class_list = data.get("command_class_list", "")

        if "multi_channel_details" in data:
            self.multi_channel_details = data.get("multi_channel_details", "")

        self.end_batch_update()

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        try:
            command_class = payload[0]
            LOGGER.debug(
                "%s - endpoint%s - update_raw - command class: 0x%02X: %s", self.prefix, endpoint, command_class, payload.hex()
            )

            match command_class:
                case ZwaveCommandClass.Basic:
                    self.parse_command_20(payload, endpoint)

                case ZwaveCommandClass.SwitchBinary:
                    self.parse_command_25(payload, endpoint)

                case ZwaveCommandClass.SwitchMultilevel:
                    self.parse_command_26(payload, endpoint)

                case ZwaveCommandClass.Meter:
                    if self._FIX_MULTICHANNEL_METER_ENDPOINT:
                        self.parse_command_32(payload, endpoint)

                case ZwaveCommandClass.MultiChannel:
                    if payload[1] == 0x0D:
                        source_endpoint = payload[2]
                        self.update_raw(payload[4:], source_endpoint)

                case ZwaveCommandClass.CentralScene:
                    self.parse_command_5b(payload, endpoint)

                case ZwaveCommandClass.ThermostatOperatingState:
                    LOGGER.debug("%s - Received ThermostatOperatingState report %s", self.prefix, payload.hex())

        except IndexError:
            LOGGER.debug("update_raw: invalid payload:%s", payload)

    def parse_command_5b(self, payload: bytes, endpoint: int) -> None:
        command = payload[1]

        service = self.service_get(CentralSceneServiceZwave, endpoint)
        if not isinstance(service, CentralSceneServiceZwave):
            LOGGER.debug("%s - CentralScene report on endpoint %s but no service", self.prefix, endpoint)
            return

        if command == 0x02:  # Supported Report
            self._parse_central_scene_supported(service, payload)
        elif command == 0x03:  # Notification
            self._parse_central_scene_notification(service, payload)

    def _parse_central_scene_supported(self, service: CentralSceneServiceZwave, payload: bytes) -> None:
        # Supported Report: [2]=supported scenes, [3]=properties, [4:]=per-scene key-attribute bitmasks.
        # properties: bit0=Identical (single bitmask for all scenes), bits1-2=bitmask bytes per scene.
        supported_scenes = payload[2]
        properties = payload[3]
        identical = bool(properties & 0x01)
        num_bitmask_bytes = (properties >> 1) & 0x03
        if num_bitmask_bytes == 0:
            return

        for scene in range(1, supported_scenes + 1):
            start = 4 if identical else 4 + (scene - 1) * num_bitmask_bytes
            bitmask = payload[start : start + num_bitmask_bytes]

            supported: list[str] = []
            for byte_index, byte in enumerate(bitmask):
                for bit in range(8):
                    if byte & (1 << bit):
                        try:
                            supported.append(CENTRAL_SCENE_EVENT_NAME[CentralSceneKeyAttribute(byte_index * 8 + bit)])
                        except ValueError:
                            continue

            service.set_supported(scene, supported)

    def _parse_central_scene_notification(self, service: CentralSceneServiceZwave, payload: bytes) -> None:
        # Notification: [2]=sequence, [3]=properties (key attribute in bits 0-2), [4]=scene number
        sequence = payload[2]
        key_attribute = payload[3] & 0x07
        scene_number = payload[4]

        try:
            event = CENTRAL_SCENE_EVENT_NAME[CentralSceneKeyAttribute(key_attribute)]
        except ValueError:
            LOGGER.debug("%s - Unknown CentralScene key attribute: 0x%02X", self.prefix, key_attribute)
            return

        service.emit_scene_event(scene_number, event, sequence)

    def parse_command_20(self, payload: bytes, endpoint: int) -> None:
        command = payload[1]

        if command == 0x03:
            light_service = self.service_get(LightServiceZwave, endpoint)
            if isinstance(light_service, LightServiceZwave):
                if light_service.supports_level():
                    light_service.level = payload[2]
                light_service.is_on = payload[2] != 0

    def parse_command_26(self, payload: bytes, endpoint: int) -> None:
        command = payload[1]

        if command == 0x03:
            light_service = self.service_get(LightServiceZwave, endpoint)
            if isinstance(light_service, LightServiceZwave):
                light_service.level = payload[2]
                light_service.is_on = payload[2] != 0

    def parse_command_25(self, payload: bytes, endpoint: int) -> None:
        command = payload[1]

        if command == 0x03:
            # Update Valve Service at specified endpoint
            valve_service = self.service_get(ValveServiceZwave, endpoint)
            if isinstance(valve_service, ValveServiceZwave):
                if payload[2] == 0xFF:
                    valve_service.is_closed = False
                elif payload[2] == 0x00:
                    valve_service.is_closed = True
                else:
                    LOGGER.warning("Unexpected Binary Switch value 0x%02X for node %s", payload[2], self.virtual_node_id)

                valve_service.is_closed = payload[2] == 0x00
                return

            # Update Siren Service at specified endpoint
            siren_service = self.service_get(SirenServiceZwave, endpoint)
            if isinstance(siren_service, SirenServiceZwave):
                if payload[2] == 0xFF:
                    siren_service._is_on = True
                elif payload[2] == 0x00:
                    siren_service._is_on = False
                else:
                    LOGGER.warning("Unexpected Binary Switch value 0x%02X for node %s", payload[2], self.virtual_node_id)
                return

            # Update Outlet Service at specified endpoint
            outlet_service = self.service_get(OutletServiceZwave, endpoint)
            if isinstance(outlet_service, OutletServiceZwave):
                outlet_service.is_on = payload[2] == 0xFF
                return

            # Update Light Service at specified endpoint
            light_service = self.service_get(LightServiceZwave, endpoint)
            if isinstance(light_service, LightServiceZwave):
                light_service.is_on = payload[2] == 0xFF
                return

            # No service found for this endpoint
            # Add new default outlet service (auto discovery)
            outlet_service = OutletServiceZwave(self, endpoint)
            outlet_service.is_on = payload[2] == 0xFF
            self.service_add(outlet_service)

    def parse_command_32(self, payload: bytes, endpoint: int) -> None:
        command = payload[1]

        # Process report
        if command == 0x02:
            props = payload[2]
            meter_type = props & 0x1F
            # rateType = (props & 0x60) >> 5
            size = payload[3] & 0x07
            scale_msb = (props & 0x80) >> 7
            scale_lsb = (payload[3] & 0x18) >> 3
            scale = (scale_msb << 2) | scale_lsb
            precision = (payload[3] & 0xE0) >> 5
            value = int.from_bytes(payload[4 : 4 + size], "big") / (10.0**precision)

            # Update Meter Service at specified endpoint
            meter_service = self.service_get(MeterServiceZwave, endpoint)
            if not isinstance(meter_service, MeterServiceZwave):
                LOGGER.error("%s - Received Meter Report for endpoint %s but no MeterService found", self.prefix, endpoint)
                return

            if meter_service.meter_type != meter_type:
                LOGGER.error(
                    "%s - Received Meter Report for meter type %s but MeterService has meter type %s",
                    self.prefix,
                    meter_type,
                    meter_service.meter_type,
                )
                return

            qolsys_scale = map_to_qolsys_meter_scale(QolsysMeterType(meter_type), scale)

            for meter in meter_service.meters:
                if meter.unit == qolsys_scale:
                    meter.value = value
                    return

    def update_automation_services(self) -> None:
        if len(self._services) > 1:
            LOGGER.debug("More than 1 one endpoint, failing back to raw zwave update")
            return

        for endpoint, services_list in self._services.items():
            for service in services_list:
                service.update_automation_service()

    async def zwave_report(self) -> None:
        for endpoint, service_list in self.services.items():
            for service in service_list:
                if isinstance(service, LightServiceZwave):
                    light_commands = [ZwaveCommandClass.SwitchBinary, ZwaveCommandClass.SwitchMultilevel]
                    for command in light_commands:
                        if command in self.command_class_list:
                            zwave_command = MQTTCommand_ZWave(
                                self._controller, self.virtual_node_id, str(service.endpoint), [command, 0x02]
                            )
                            await zwave_command.send_command()

                if isinstance(service, LockServiceZwave):
                    lock_commands = [ZwaveCommandClass.DoorLock]
                    for command in lock_commands:
                        if command in self.command_class_list:
                            zwave_command = MQTTCommand_ZWave(
                                self._controller, self.virtual_node_id, str(service.endpoint), [command, 0x02]
                            )
                            await zwave_command.send_command()

                if isinstance(service, ThermostatServiceZwave):
                    thermostat_commands = [
                        ZwaveCommandClass.ThermostatFanMode,
                        ZwaveCommandClass.ThermostatMode,
                        ZwaveCommandClass.ThermostatSetPoint,
                        ZwaveCommandClass.ThermostatOperatingState,
                    ]
                    for command in thermostat_commands:
                        if command in self.command_class_list:
                            zwave_command = MQTTCommand_ZWave(
                                self._controller, self.virtual_node_id, str(service.endpoint), [command, 0x02]
                            )
                            await zwave_command.send_command()

                if isinstance(service, ValveServiceZwave):
                    valve_commands = [ZwaveCommandClass.SwitchBinary]
                    for command in valve_commands:
                        if command in self.command_class_list:
                            zwave_command = MQTTCommand_ZWave(
                                self._controller, self.virtual_node_id, str(service.endpoint), [command, 0x02]
                            )
                            await zwave_command.send_command()

                if isinstance(service, SirenServiceZwave):
                    siren_commands = [ZwaveCommandClass.SwitchBinary]
                    for command in siren_commands:
                        if command in self.command_class_list:
                            zwave_command = MQTTCommand_ZWave(
                                self._controller, self.virtual_node_id, str(service.endpoint), [command, 0x02]
                            )
                            await zwave_command.send_command()

                if isinstance(service, OutletServiceZwave):
                    if ZwaveCommandClass.SwitchBinary in self.command_class_list:
                        zwave_command = MQTTCommand_ZWave(
                            self._controller,
                            self.virtual_node_id,
                            str(service.endpoint),
                            [ZwaveCommandClass.SwitchBinary, 0x02],
                        )
                        await zwave_command.send_command()

                if isinstance(service, CentralSceneServiceZwave):
                    if ZwaveCommandClass.CentralScene in self.command_class_list:
                        LOGGER.debug("%s - endpoint%s - sending central_scene_supported_get", self.prefix, service.endpoint)
                        await self._controller.commands.zwave.central_scene_supported_get(
                            self.virtual_node_id, str(service.endpoint)
                        )

    def to_dict_zwave(self) -> dict[str, str]:
        return {
            "_id": self._id,
            "node_id": self._node_id,
            "node_name": self._node_name,
            "node_type": self._node_type,
            "node_status": self._node_status,
            "partition_id": self._partition_id,
            "node_secure_cmd_cls": self._node_secure_cmd_cls,
            "node_battery_level": self._node_battery_level,
            "node_battery_level_value": self._node_battery_level_value,
            "is_node_listening_node": self._is_node_listening_node,
            "basic_report_value": self._basic_report_value,
            "switch_multilevel_report_value": self._switch_multilevel_report_value,
            "basic_device_type": self._basic_device_type,
            "generic_device_type": self._generic_device_type,
            "specific_device_type": self._specific_device_type,
            "num_secure_command_class": self._num_secure_command_class,
            "secure_command_class": self._secure_command_class,
            "manufacture_id": self._manufacture_id,
            "product_type": self._product_type,
            "device_protocol": self._device_protocol,
            "paired_status": self._paired_status,
            "is_device_sleeping": self._is_device_sleeping,
            "is_device_hidden": self._is_device_hidden,
            "last_updated_date": self._last_updated_date,
            "command_class_list": self._command_class_list,
            "multisensor_capabilities": self._multisensor_capabilities,
            "notification_capabilities": self._notification_capabilities,
            "multi_channel_details": self._multi_channel_details,
            "endpoint": self._endpoint,
            "endpoint_details": self._endpoint_details,
            "meter_capabilities": self._meter_capabilities,
        }

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def generic_device_type(self) -> ZwaveDeviceClass:
        try:
            dict = json.loads(self.extras)
            generic_type = int(dict.get("GENERIC_TYPE", "0"))
            return ZwaveDeviceClass(generic_type)
        except (ValueError, TypeError, json.JSONDecodeError):
            return ZwaveDeviceClass.Unknown

    @property
    def command_class_list(self) -> list[ZwaveCommandClass]:
        commands = []
        array = self._command_class_list.strip("[]").split(",")
        for command in array:
            try:
                commands.append(ZwaveCommandClass(int(command)))
            except (ValueError, TypeError):
                continue
        return commands

    @command_class_list.setter
    def command_class_list(self, value: str) -> None:
        if self._command_class_list != value:
            self._command_class_list = value

            # Update services on root endpoint (0) based on command class list
            endpoint = 0

            # Add root central scene service
            if ZwaveCommandClass.CentralScene in self.command_class_list:
                if self.service_get(CentralSceneServiceZwave, endpoint) is None:
                    self.service_add_central_scene_service(endpoint=endpoint)

    @property
    def secure_command_class_list(self) -> list[ZwaveCommandClass]:
        commands = []
        array = self._node_secure_cmd_cls.strip("[]").split(",")
        for command in array:
            try:
                commands.append(ZwaveCommandClass(int(command)))
            except (ValueError, TypeError):
                continue
        return commands

    @property
    def multisensor_capabilities(self) -> str:
        return self._multisensor_capabilities

    @multisensor_capabilities.setter
    def multisensor_capabilities(self, value: str) -> None:
        if self._multisensor_capabilities != value:
            self._multisensor_capabilities = value

            # Update Sensor Service
            try:
                sensors_dict = json.loads(value)
                for endpoint, values in sensors_dict.items():
                    service = self.service_get(SensorService, int(endpoint))
                    if not service:
                        service = SensorServiceZwave(self, int(endpoint))
                        self.service_add(service)

                    if isinstance(service, SensorServiceZwave):
                        service.update_zwave_service(values)

            except json.JSONDecodeError:
                LOGGER.error("%s - Error parsing multilevelsensor_capabilities:%s", self.prefix)
                return

    @property
    def meter_capabilities(self) -> str:
        return self._meter_capabilities

    @meter_capabilities.setter
    def meter_capabilities(self, value: str) -> None:
        # Do not update meters if FIX_MULTICHANNEL_METER_ENDPOINT is enabled
        if self._FIX_MULTICHANNEL_METER_ENDPOINT:
            return

        if self._meter_capabilities != value:
            self._meter_capabilities = value

            # Update Meter Service
            try:
                meters_dict = json.loads(value)
                if len(meters_dict.keys()) > 1 and not self._FIX_MULTICHANNEL_METER_ENDPOINT:
                    self._FIX_MULTICHANNEL_METER_ENDPOINT = True
                    LOGGER.debug(
                        "%s - Multiple meter endpoints detected, enabling FIX_MULTICHANNEL_METER_ENDPOINT", self.prefix
                    )

                for endpoint, values in meters_dict.items():
                    service = self.service_get(MeterService, int(endpoint))
                    if not service:
                        service = MeterServiceZwave(self, int(endpoint))
                        self.service_add(service)

                    if isinstance(service, MeterServiceZwave):
                        service.update_zwave_service(values, not self._FIX_MULTICHANNEL_METER_ENDPOINT)

            except json.JSONDecodeError:
                LOGGER.error("%s - Error parsing meter_capabilities:%s", self.prefix)
                return

    @property
    def multi_channel_details(self) -> str:
        return self._multi_channel_details

    @multi_channel_details.setter
    def multi_channel_details(self, value: str) -> None:
        # parse endpoint dict and add new services
        if self._multi_channel_details != value:
            self._multi_channel_details = value

            try:
                details: dict[str, int | list[int]] = json.loads(value) if isinstance(value, str) and value.strip() else {}
            except json.JSONDecodeError:
                details = {}

            if not isinstance(details, dict):
                details = {}

            endpoints: dict[int, list[int]] = {int(k): v for k, v in details.items() if k.isdigit() and isinstance(v, list)}

            for ep, command_classes in sorted(endpoints.items()):
                if ZwaveCommandClass.SwitchMultilevel in command_classes:
                    if self.service_get(LightServiceZwave, ep) is None:
                        self.service_add_light_service(endpoint=ep)

                if ZwaveCommandClass.SwitchBinary in command_classes:
                    # check if a service is already regisrered with pannel
                    if (
                        self.service_get(ValveServiceZwave, ep) is None
                        and self.service_get(LightServiceZwave, ep) is None
                        and self.service_get(SirenServiceZwave, ep) is None
                    ):
                        # Add new Binary switch
                        self.service_add_outlet_service(endpoint=ep)

                if ZwaveCommandClass.CentralScene in command_classes:
                    # Add central scene service; discovery is sent later in zwave_report
                    if self.service_get(CentralSceneServiceZwave, ep) is None:
                        self.service_add_central_scene_service(endpoint=ep)

    @property
    def node_status(self) -> str:
        return self._node_status

    @node_status.setter
    def node_status(self, value: str) -> None:
        if self._node_status != value:
            self._node_status = value
            for service in self.service_get_protocol(StatusServiceZwave):
                if isinstance(service, StatusServiceZwave):
                    service.update_automation_service()
