import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.device import QolsysAutomationDevice
from qolsys_controller.enum_zwave import ZwaveCommandClass, ZwaveDeviceClass

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController


LOGGER = logging.getLogger(__name__)


class QolsysAutomationDeviceZwave(QolsysAutomationDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str], dict: dict[str, str]) -> None:
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
        self._command_class_list: str = zwave_dict.get("command_class_list", "")
        self._meter_capabilities: str = ""
        self._multisensor_capabilities: str = ""
        self._notification_capabilities = zwave_dict.get("notification_capabilities", "")
        self._multi_channel_details = zwave_dict.get("multi_channel_details", "")
        self._endpoint = zwave_dict.get("endpoint", "")
        self._endpoint_details = zwave_dict.get("endpoint_details", "")

        # Add Base Services
        self.service_add_status_service(endpoint=0)
        self.service_add_battery_service(endpoint=0)

        super().update_automation_services()

    def update_zwave_device(self, data: dict[str, str]) -> None:
        pass

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
        array = self._nodeid_cmd_classes.strip("[]").split(",")
        for command in array:
            try:
                commands.append(ZwaveCommandClass(int(command)))
            except (ValueError, TypeError):
                continue
        return commands
