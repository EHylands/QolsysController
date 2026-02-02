import json
import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.device import QolsysAutomationDevice
from qolsys_controller.enum_zwave import ZwaveCommandClass, ZwaveDeviceClass

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController


LOGGER = logging.getLogger(__name__)


class QolsysAutomationDeviceZwave(QolsysAutomationDevice):
    def __init__(self, controller: "QolsysController", dict: dict[str, str]) -> None:
        super().__init__(controller, dict)

        # Add Z-Wave Services
        self.service_add_battery_service(endpoint=0)
        self.service_add_status_service(endpoint=0)

        super().update_automation_services()

    def update_zwave_device(self, data: dict[str, str]) -> None:
        pass

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
