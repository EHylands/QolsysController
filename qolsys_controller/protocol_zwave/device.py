import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.enum_zwave import (
    ZwaveCommandClass,
    ZwaveDeviceClass,
    ZWaveMultilevelSensorScale,
)
from qolsys_controller.mqtt_command import MQTTCommand_ZWave
from qolsys_controller.observable import QolsysObservable
from qolsys_controller.protocol_zwave.service_meter import QolsysZwaveServiceMeter
from qolsys_controller.protocol_zwave.service_multilevelsensor import (
    QolsysZwaveMultilevelSensor,
    QolsysZwaveServiceMultilevelSensor,
)

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysZWaveDevice(QolsysObservable):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__()

        self._controller = controller

        self._id: str = zwave_dict.get("_id", "")
        self._node_id: str = zwave_dict.get("node_id", "")
        self._node_name: str = zwave_dict.get("node_name", "")
        self._node_type: str = zwave_dict.get("node_type", "")
        self._node_status: str = zwave_dict.get("node_status", "")
        self._partition_id: str = zwave_dict.get("partition_id", "")
        self._node_secure_cmd_cls: str = zwave_dict.get("node_secure_cmd_cls", "")
        self._node_battery_level: str = zwave_dict.get("node_battery_level", "")
        self._node_battery_level_value: str = zwave_dict.get("node_battery_level_value", "")
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
        self._command_class_list: str = zwave_dict.get("command_class_list", "")
        self._meter_capabilities: str = ""
        self._multisensor_capabilities: str = ""
        self._notification_capabilities = zwave_dict.get("notification_capabilities", "")
        self._multi_channel_details = zwave_dict.get("multi_channel_details", "")
        self._endpoint = zwave_dict.get("endpoint", "")
        self._endpoint_details = zwave_dict.get("endpoint_details", "")

        # Set Meter and MutilevelSensor Services if available
        self._FIX_MULTICHANNEL_METER_ENDPOINT: bool = False
        self._meter_endpoints: list[QolsysZwaveServiceMeter] = []
        self._multilevelsensor_endpoints: list[QolsysZwaveServiceMultilevelSensor] = []
        self.meter_capabilities = zwave_dict.get("meter_capabilities", "")
        self.multisensor_capabilities = zwave_dict.get("multisensor_capabilities", "")

    def parse32(self, payload: bytes, endpoint: int) -> None:
        command_class = payload[0]
        command = payload[1]

        if command_class != ZwaveCommandClass.Meter:
            LOGGER.debug("0x32: Invalid command class")
            return

        # Process report
        if command == 0x02:
            props = payload[2]
            meter_type = props & 0x1F
            # meter_type = (props >> 5) & 0x07
            # rateType = (props & 0x60) >> 5
            size = payload[3] & 0x07
            scale_msb = (props & 0x80) >> 7
            scale_lsb = (payload[3] & 0x18) >> 3
            scale = (scale_msb << 2) | scale_lsb
            precision = (payload[3] & 0xE0) >> 5
            value = int.from_bytes(payload[4 : 4 + size], byteorder="big") / pow(10, precision)

            for meter_endpoint in self.meter_endpoints:
                if int(meter_endpoint.endpoint) == endpoint and meter_endpoint.meter_type == meter_type:
                    for sensor in meter_endpoint.sensors:
                        if sensor.scale == scale:
                            sensor.value = value

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        LOGGER.debug("Raw Update (node%s-%s) - payload: %s", self.node_id, endpoint, payload.hex())

        try:
            command_class = payload[0]

            match command_class:
                case ZwaveCommandClass.Meter:
                    if not self._FIX_MULTICHANNEL_METER_ENDPOINT:
                        return

                    self.parse32(payload, endpoint)

                case ZwaveCommandClass.MultiChannel:
                    if payload[1] == 0x0D:
                        source_endpoint = payload[2]
                        self.update_raw(payload[4:], source_endpoint)

        except IndexError:
            LOGGER.debug("update_raw: invalid payload:%s", payload)

    async def zwave_report(self) -> None:
        command_array = [
            ZwaveCommandClass.SwitchBinary,
            ZwaveCommandClass.SwitchMultilevel,
            ZwaveCommandClass.ThermostatFanMode,
            ZwaveCommandClass.ThermostatMode,
            ZwaveCommandClass.ThermostatSetPoint,
            ZwaveCommandClass.DoorLock,
        ]

        for command in command_array:
            if command in self.command_class_list:
                zwave_command = MQTTCommand_ZWave(self._controller, self.node_id, "0", [command, 0x02])
                await zwave_command.send_command()

    def update_base(self, data: dict[str, str]) -> None:  # noqa: C901, PLR0912, PLR0915
        # Check if we are updating same node_id
        node_id_update = data.get("node_id", "")
        if node_id_update != self._node_id:
            LOGGER.error(
                "Updating ZWave%s (%s) with ZWave%s (different node_id)",
                self.node_id,
                self.node_name,
                node_id_update,
            )
            return

        self.start_batch_update()

        if "paired_status" in data:
            self.paired_status = data.get("paired_status", "")
        if "node_battery_level" in data:
            self.node_battery_level = data.get("node_battery_level", "")
        if "node_battery_level_value" in data:
            self.node_battery_level_value = data.get("node_battery_level_value", "")
        if "node_status" in data:
            self.node_status = data.get("node_status", "")
        if "node_name" in data:
            self.node_name = data.get("node_name", "")
        if "node_type" in data:
            self.node_type = data.get("node_type", "")
        if "partition_id" in data:
            self.partition_id = data.get("partition_id", "")
        if "node_secure_cmd_cls" in data:
            self._node_secure_cmd_cls = data.get("node_secure_cmd_cls", "")
        if "is_node_listening_node" in data:
            self._is_node_listening_node = data.get("is_node_listening_node", "")
        if "basic_report_value" in data:
            self._basic_report_value = data.get("basic_report_value", "")
        if "switch_multilevel_report_value" in data:
            self._switch_multilevel_report_value = data.get("switch_multilevel_report_value", "")
        if "basic_device_type" in data:
            self._basic_device_type = data.get("basic_device_type", "")
        if "generic_device_type" in data:
            self._generic_device_type = data.get("generic_device_type", "")
        if "specific_device_type" in data:
            self._specific_device_type = data.get("specific_device_type", "")
        if "num_secure_command_class" in data:
            self._num_secure_command_class = data.get("num_secure_command_class", "")
        if "secure_command_class" in data:
            self._secure_command_class = data.get("secure_command_class", "")
        if "manufacture_id" in data:
            self._manufacture_id = data.get("manufacture_id", "")
        if "product_type" in data:
            self._product_type = data.get("product_type", "")
        if "device_protocol" in data:
            self._device_protocol = data.get("device_protocol", "")
        if "paired_status" in data:
            self.paired_status = data.get("paired_status", "")
        if "is_device_sleeping" in data:
            self._is_device_sleeping = data.get("is_device_sleeping", "")
        if "is_device_hidden" in data:
            self._is_device_hidden = data.get("is_device_hidden", "")
        if "last_updated_date" in data:
            self._last_updated_date = data.get("last_updated_date", "")
        if "command_class_list" in data:
            self._command_class_list = data.get("command_class_list", "")
        if "multisensor_capabilities" in data:
            self.multisensor_capabilities = data.get("multisensor_capabilities", "")
        if "meter_capabilities" in data:
            self.meter_capabilities = data.get("meter_capabilities", "")
        if "notification_capabilities" in data:
            self._notification_capabilities = data.get("notification_capabilities", "")
        if "multi_channel_details" in data:
            self._multi_channel_details = data.get("multi_channel_details", "")
        if "endpoint" in data:
            self.endpoint = data.get("endpoint", "")
        if "endpoint_details" in data:
            self.endpoint_details = data.get("endpoint_details", "")

        self.end_batch_update()

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def node_id(self) -> str:
        return self._node_id

    @node_id.setter
    def node_id(self, value: str) -> None:
        self._node_id = value

    @property
    def paired_status(self) -> str:
        return self._paired_status

    @paired_status.setter
    def paired_status(self, value: str) -> None:
        if self._paired_status != value:
            LOGGER.debug("ZWave%s (%s) - paired_status: %s", self.node_id, self.node_name, value)
            self._paired_status = value
            self.notify()

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

    @property
    def node_battery_level(self) -> str:
        return self._node_battery_level

    @node_battery_level.setter
    def node_battery_level(self, value: str) -> None:
        if self._node_battery_level != value:
            LOGGER.debug("ZWave%s (%s) - node_battery_level: %s", self.node_id, self.node_name, value)
            self._node_battery_level = value
            self.notify()

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        if self._endpoint != value:
            self._endpoint = value
            LOGGER.debug("ZWave%s (%s) - endpoint: %s", self.node_id, self.node_name, value)

    @property
    def endpoint_details(self) -> str:
        return self._endpoint_details

    @endpoint_details.setter
    def endpoint_details(self, value: str) -> None:
        if self._endpoint_details != value:
            self._endpoint_details = value
            LOGGER.debug("ZWave%s (%s) - endpoint_details: %s", self.node_id, self.node_name, value)

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
            LOGGER.debug("ZWave%s (%s) - meter_capabilities: %s", self.node_id, self.node_name, value)

            # Update Meter Service
            try:
                meter_services = json.loads(value)

                if len(meter_services.keys()) > 1 and not self._FIX_MULTICHANNEL_METER_ENDPOINT:
                    self._FIX_MULTICHANNEL_METER_ENDPOINT = True
                    LOGGER.debug("ZWave%s - FIX_MULTICHANNEL_METER_ENPOINT = True", self.node_id)

                for endpoint, service in meter_services.items():
                    # Check if we already have this meter service
                    meter_endpoint = None
                    for meter in self._meter_endpoints:
                        if meter.endpoint == endpoint:
                            meter_endpoint = meter
                            meter_endpoint.update_iq2medi(service)
                            break

                    # Create new meter service if not found
                    if meter_endpoint is None:
                        LOGGER.debug("ZWave%s (%s) - Adding meter endpoint%s", self.node_id, self.node_name, endpoint)
                        meter_endpoint = QolsysZwaveServiceMeter(self, endpoint, service)
                        self._meter_endpoints.append(meter_endpoint)

                        if not self._FIX_MULTICHANNEL_METER_ENDPOINT:
                            meter_endpoint.update_iq2medi(service)

            except json.JSONDecodeError:
                LOGGER.error("ZWave%s (%s) - Error parsing meter_capabilities:%s", self.node_id, self.node_name, value)
                return

    @property
    def multisensor_capabilities(self) -> str:
        return self._multisensor_capabilities

    @multisensor_capabilities.setter
    def multisensor_capabilities(self, value: str) -> None:
        if self._multisensor_capabilities != value:
            self._multisensor_capabilities = value

            # Update Multilevel Sensor Service
            try:
                sensor_services = json.loads(value)
                for endpoint, service in sensor_services.items():
                    # Check if we already have this meter service
                    sensor_endpoint = None
                    for sensor in self._multilevelsensor_endpoints:
                        if sensor.endpoint == endpoint:
                            sensor_endpoint = sensor
                            sensor_endpoint.update_iq2medi(service)
                            break

                    # Create new meter service if not found
                    if sensor_endpoint is None:
                        LOGGER.debug(
                            "ZWave%s (%s) - Adding multilevelsensor endpoint%s", self.node_id, self.node_name, endpoint
                        )
                        sensor_endpoint = QolsysZwaveServiceMultilevelSensor(self, endpoint, service)
                        self.multilevelsensor_endpoints.append(sensor_endpoint)

            except json.JSONDecodeError:
                LOGGER.error(
                    "ZWave%s (%s) - Error parsing multilevelsensor_capabilities:%s", self.node_id, self.node_name, value
                )
                return

    @property
    def node_battery_level_value(self) -> int | None:
        try:
            value = int(self._node_battery_level_value)
            if value >= 0 and value <= 100:
                return value
            else:
                return None

        except ValueError:
            return None

    @node_battery_level_value.setter
    def node_battery_level_value(self, value: str) -> None:
        if self._node_battery_level_value != value:
            LOGGER.debug("ZWave%s (%s) - node_battery_level_value: %s", self.node_id, self.node_name, value)
            self._node_battery_level_value = value
            self.notify()

    @property
    def node_status(self) -> str:
        return self._node_status

    @node_status.setter
    def node_status(self, value: str) -> None:
        if self._node_status != value:
            LOGGER.debug("ZWave%s (%s) - node_status: %s", self.node_id, self.node_name, value)
            self._node_status = value
            self.notify()

    @property
    def node_name(self) -> str:
        return self._node_name

    @node_name.setter
    def node_name(self, value: str) -> None:
        if self._node_name != value:
            LOGGER.debug("ZWave%s (%s) - node_name: %s", self.node_id, self.node_name, value)
            self._node_name = value
            self.notify()

    @property
    def node_type(self) -> str:
        return self._node_type

    @node_type.setter
    def node_type(self, value: str) -> None:
        if self._node_type != value:
            LOGGER.debug("ZWave%s (%s) - node_type: %s", self.node_id, self.node_name, value)
            self._node_type = value
            self.notify()

    @property
    def partition_id(self) -> str:
        return self._partition_id

    @partition_id.setter
    def partition_id(self, value: str) -> None:
        if self._partition_id != value:
            LOGGER.debug("ZWave%s (%s) - partition_id: %s", self._node_id, self._node_name, value)
            self._partition_id = value
            self.notify()

    @property
    def meter_endpoints(self) -> list[QolsysZwaveServiceMeter]:
        return self._meter_endpoints

    @property
    def multilevelsensor_endpoints(self) -> list[QolsysZwaveServiceMultilevelSensor]:
        return self._multilevelsensor_endpoints

    @property
    def generic_device_type(self) -> ZwaveDeviceClass:
        try:
            return ZwaveDeviceClass(int(self._generic_device_type))
        except ValueError:
            return ZwaveDeviceClass.Unknown

    def is_battery_enabled(self) -> bool:
        return self.node_battery_level_value is not None

    def is_service_meter_enabled(self) -> bool:
        return self._meter_endpoints != []

    def is_service_multilevelsensor_enabled(self) -> bool:
        return self._multilevelsensor_endpoints != []

    def multilevelsensor_value(self, scale: ZWaveMultilevelSensorScale) -> list[QolsysZwaveMultilevelSensor]:
        result: list[QolsysZwaveMultilevelSensor] = []
        for endpoint in self.multilevelsensor_endpoints:
            sensor = endpoint.get_sensor(scale)
            if sensor is not None:
                result.append(sensor)
        return result

    def to_dict_base(self) -> dict[str, str]:
        return {
            "_id": self._id,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "node_status": self.node_status,
            "partition_id": self._partition_id,
            "node_battery_level": self.node_battery_level,
            "node_battery_level_value": self._node_battery_level_value,
            "paired_status": self.paired_status,
            "node_secure_cmd_cls": self._node_secure_cmd_cls,
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
            "is_device_sleeping": self._is_device_sleeping,
            "is_device_hidden": self._is_device_hidden,
            "last_updated_date": self._last_updated_date,
            "command_class_list": self._command_class_list,
            "multisensor_capabilities": self.multisensor_capabilities,
            "meter_capabilities": self.meter_capabilities,
            "notification_capabilities": self._notification_capabilities,
            "multi_channel_details": self._multi_channel_details,
            "endpoint": self._endpoint,
            "endpoint_details": self._endpoint_details,
        }
