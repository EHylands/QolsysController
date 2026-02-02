import logging
from abc import ABC
from typing import TYPE_CHECKING

from qolsys_controller.automation.protocol_battery import BatteryProtocol
from qolsys_controller.automation.protocol_light import LightProtocol
from qolsys_controller.automation.protocol_lock import LockProtocol
from qolsys_controller.automation.protocol_service import ServiceProtocol
from qolsys_controller.automation.protocol_status import StatusProtocol
from qolsys_controller.automation.service import AutomationService
from qolsys_controller.automation.service_status import StatusService
from qolsys_controller.automation_powerg.service_battery import BatteryServicePowerG
from qolsys_controller.automation_powerg.service_lock import LockServicePowerG
from qolsys_controller.automation_zwave.service_battery import BatteryServiceZwave
from qolsys_controller.automation_zwave.service_light import LightServiceZwave
from qolsys_controller.automation_zwave.service_status import StatusServiceZwave
from qolsys_controller.enum import AutomationDeviceProtocol
from qolsys_controller.observable import QolsysObservable

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysAutomationDevice(QolsysObservable, ABC):
    def __init__(self, controller: "QolsysController", dict: dict[str, str]) -> None:
        super().__init__()

        self._controller: QolsysController = controller

        # Main device identifier
        self._virtual_node_id: str = dict.get("virtual_node_id", "")

        self._id: str = dict.get("_id", "")
        self._partition_id: str = dict.get("partition_id", "")
        self._device_id: str = dict.get("device_id", "")
        self._device_name: str = dict.get("device_name", "")
        self._device_type: str = dict.get("device_type", "")
        self._extras: str = dict.get("extras", "")
        self._protocol: str = dict.get("protocol", "")
        self._state: str = dict.get("state", "")
        self._status: str = dict.get("status", "")
        self._version: str = dict.get("version", "")
        self._end_point: str = dict.get("end_point", "")
        self._is_autolocking_enabled: str = dict.get("is_autolocking_enabled", "")
        self._endpoint_secure_cmd_classes: str = dict.get("endpoint_secure_cmd_classes", "")
        self._automation_id: str = dict.get("automation_id", "")
        self._node_battery_level_value: str = dict.get("node_battery_level_value", "")
        self._last_updated_date: str = dict.get("last_updated_date", "")
        self._manufacturer_id: str = dict.get("manufacturer_id", "")
        self._endpoint_cmd_classes: str = dict.get("endpoint_cmd_classes", "")
        self._nodeid_cmd_classes: str = dict.get("nodeid_cmd_classes", "")
        self._is_device_hidden: str = dict.get("is_device_hidden", "")
        self._nodeid_secure_cmd_classes: str = dict.get("nodeid_secure_cmd_classes", "")
        self._created_date: str = dict.get("created_date", "")
        self._smart_energy_optimizer: str = dict.get("smart_energy_optimizer", "")
        self._linked_security_zone: str = dict.get("linked_security_zone", "")

        self._services: list[AutomationService] = []

        match self.device_type:
            case "Light":
                self.service_add_light_service(int(self._end_point))
            case "Door Lock":
                self.service_add_lock_service(int(self._end_point))

    def info(self) -> None:
        pass
        # return  "AutDev%s [%s] (%s)" % (self.virtual_node_id, self.protocol, self.device_name)

    def service_get(self, service_type: type[ServiceProtocol], endpoint: int = 0) -> ServiceProtocol | None:
        for service in self._services:
            if isinstance(service, service_type) and service.endpoint == endpoint:
                return service
        return None

    def service_get_protocol(self, service_type: type[ServiceProtocol]) -> list[AutomationService]:
        services: list[AutomationService] = []
        for service in self._services:
            if isinstance(service, service_type):
                services.append(service)
        return services

    def service_add(self, service: AutomationService) -> None:
        if not isinstance(service, ServiceProtocol):
            LOGGER.error(
                "AutDev%s [%s][%s][%s] (%s) - Unable to add Service (not a ServiceProtocol): %s",
                self.virtual_node_id,
                self.protocol,
                self.virtual_node_id,
                service.endpoint,
                self.device_name,
                type(service),
            )
            return

        if isinstance(service, LightProtocol):
            self._services.append(service)
            LOGGER.debug(
                "AutDev%s [%s][%s][%s] (%s) - Adding Light Service ",
                self.virtual_node_id,
                self.protocol,
                self.virtual_node_id,
                service.endpoint,
                self.device_name,
            )
            return

        if isinstance(service, BatteryProtocol):
            self._services.append(service)
            LOGGER.debug(
                "AutDev%s [%s][%s][%s] (%s) - Adding Battery Service ",
                self.virtual_node_id,
                self.protocol,
                self.virtual_node_id,
                service.endpoint,
                self.device_name,
            )
            return

        if isinstance(service, LockProtocol):
            self._services.append(service)
            LOGGER.debug(
                "AutDev%s [%s][%s][%s] (%s) - Adding Lock Service ",
                self.virtual_node_id,
                self.protocol,
                self.virtual_node_id,
                service.endpoint,
                self.device_name,
            )
            return

        if isinstance(service, StatusProtocol):
            self._services.append(service)
            LOGGER.debug(
                "AutDev%s [%s][%s][%s] (%s) - Adding Status Service ",
                self.virtual_node_id,
                self.protocol,
                self.virtual_node_id,
                service.endpoint,
                self.device_name,
            )
            return

        LOGGER.error(
            "AutDev%s [%s][%s][%s] (%s) - Unable to add Service (unknown type): %s",
            self.virtual_node_id,
            self.protocol,
            self.virtual_node_id,
            service.endpoint,
            self.device_name,
            type(service),
        )

    def service_add_light_service(self, endpoint: int = 0) -> None:
        light_service: AutomationService | None = None

        match self.protocol:
            case AutomationDeviceProtocol.POWERG:
                pass
            case AutomationDeviceProtocol.Z_WAVE:
                light_service = LightServiceZwave(automation_device=self, endpoint=endpoint)

        if light_service is not None:
            self.service_add(light_service)
            return

        LOGGER.error(
            "AutDev%s [%s][%s][%s] (%s) - Unable to add Light Service",
            self.virtual_node_id,
            self.protocol,
            self.virtual_node_id,
            endpoint,
            self.device_name,
        )

    def service_add_lock_service(self, endpoint: int = 0) -> None:
        lock_service: AutomationService | None = None
        if self.protocol == AutomationDeviceProtocol.POWERG:
            lock_service = LockServicePowerG(self, endpoint=endpoint)

        if lock_service is not None:
            self.service_add(lock_service)
            return

        LOGGER.error(
            "AutDev%s [%s][%s][%s] (%s) - Unable to add Lock Service",
            self.virtual_node_id,
            self.protocol,
            self.virtual_node_id,
            endpoint,
            self.device_name,
        )

    def service_add_battery_service(self, endpoint: int = 0) -> None:
        battery_service: AutomationService | None = None
        if self.protocol == AutomationDeviceProtocol.POWERG:
            battery_service = BatteryServicePowerG(automation_device=self, endpoint=endpoint)

        if self.protocol == AutomationDeviceProtocol.Z_WAVE:
            battery_service = BatteryServiceZwave(automation_device=self, endpoint=endpoint)

        if battery_service is not None:
            self.service_add(battery_service)
            return

        LOGGER.error(
            "AutDev%s [%s][%s][%s] (%s) - Unable to add Battery Service",
            self.virtual_node_id,
            self.protocol,
            self.virtual_node_id,
            endpoint,
            self.device_name,
        )

    def service_add_status_service(self, endpoint: int = 0) -> None:
        service: StatusService | None = None

        match self.protocol:
            case AutomationDeviceProtocol.POWERG:
                pass

            case AutomationDeviceProtocol.Z_WAVE:
                service = StatusServiceZwave(automation_device=self, endpoint=endpoint)

        if service is not None:
            self.service_add(service)
            return

    def update_automation_services(self) -> None:
        for service in self._services:
            service.update_automation_service()

    def update_automation_device(self, data: dict[str, str]) -> None:
        # Check if we are updating same virtual_node_id
        virtual_node_id_update = data.get("virtual_node_id", "")
        if virtual_node_id_update != self._virtual_node_id:
            LOGGER.error(
                "Updating AutDev%s (%s) with %s (different virtual_node_id)",
                self._virtual_node_id,
                self._device_name,
                virtual_node_id_update,
            )
            return

        self.start_batch_update()

        if "device_name" in data:
            self._device_name = data.get("device_name", "")

        if "partition_id" in data:
            self._partition_id = data.get("partition_id", "")

        if "state" in data:
            self._state = data.get("state", "")

        if "status" in data:
            self._status = data.get("status", "")

        if "extras" in data:
            self.extras = data.get("extras", "")

        self.update_automation_services()

        self.end_batch_update()

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def controller(self) -> "QolsysController":
        return self._controller

    @property
    def services(self) -> list[AutomationService]:
        return self._services

    @property
    def prefix(self) -> str:
        return f"AutDev{self.virtual_node_id} ({self.device_name}) [{self.protocol}][{self.virtual_node_id}]"

    @property
    def device_id(self) -> str:
        return self._device_id

    @device_id.setter
    def device_id(self, value: str) -> None:
        if self._device_id != value:
            LOGGER.debug("AutDev%s (%s) - device_id: %s", self.device_id, self.device_name, value)
            self._device_id = value
            self.notify()

    @property
    def virtual_node_id(self) -> str:
        return self._virtual_node_id

    @virtual_node_id.setter
    def virtual_node_id(self, value: str) -> None:
        if self._virtual_node_id != value:
            LOGGER.debug("AutDev%s (%s) - virtual_node_id: %s", self.device_id, self.device_name, value)
            self._virtual_node_id = value
            self.notify()

    @property
    def partition_id(self) -> str:
        return self._partition_id

    @partition_id.setter
    def partition_id(self, value: str) -> None:
        if self._partition_id != value:
            LOGGER.debug("AutDev%s (%s) - partition_id: %s", self.device_id, self.device_name, value)
            self._partition_id = value
            self.notify()

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        if self._state != value:
            # LOGGER.debug("AutDev%s (%s) - state: %s", self.device_id, self.device_name, value)
            self._state = value
            self.notify()

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        if self._status != value:
            # LOGGER.debug("AutDev%s (%s) - status: %s", self.device_id, self.device_name, value)
            self._status = value
            self.notify()

    @property
    def device_name(self) -> str:
        return self._device_name

    @device_name.setter
    def device_name(self, value: str) -> None:
        if self._device_name != value:
            LOGGER.debug("AutDev%s (%s) - device_name: %s", self.device_id, self.device_name, value)
            self._device_name = value
            self.notify()

    @property
    def device_type(self) -> str:
        return self._device_type

    @device_type.setter
    def device_type(self, value: str) -> None:
        if self._device_type != value:
            LOGGER.debug("AutDev%s (%s) - device_type: %s", self.device_id, self.device_name, value)
            self._device_type = value
            self.notify()

    @property
    def extras(self) -> str:
        return self._extras

    @extras.setter
    def extras(self, value: str) -> None:
        if self._extras != value:
            # LOGGER.debug("AutDev%s (%s) - extras: %s", self.device_id, self.device_name, value)
            self._extras = value
            self.notify()

    @property
    def protocol(self) -> AutomationDeviceProtocol:
        try:
            return AutomationDeviceProtocol(self._protocol)
        except ValueError:
            return AutomationDeviceProtocol.UNKNOWN

    @protocol.setter
    def protocol(self, value: str) -> None:
        if self._protocol != value:
            LOGGER.debug("AutDev%s (%s) - protocol: %s", self.device_id, self.device_name, value)
            self._protocol = value
            self.notify()

    def to_dict(self) -> dict[str, str]:
        return {
            "_id": self._id,
            "virtual_node_id": self._virtual_node_id,
            "partition_id": self._partition_id,
            "device_id": self._device_id,
            "device_name": self._device_name,
            "device_type": self._device_type,
            "protocol": self._protocol,
            "state": self._state,
            "status": self._status,
            "version": self._version,
            "end_point": self._end_point,
            "is_autolocking_enabled": self._is_autolocking_enabled,
            "endpoint_secure_cmd_classes": self._endpoint_secure_cmd_classes,
            "automation_id": self._automation_id,
            "node_battery_level_value": self._node_battery_level_value,
            "last_updated_date": self._last_updated_date,
            "manufacturer_id": self._manufacturer_id,
            "endpoint_cmd_classes": self._endpoint_cmd_classes,
            "nodeid_cmd_classes": self._nodeid_cmd_classes,
            "is_device_hidden": self._is_device_hidden,
            "nodeid_secure_cmd_classes": self._nodeid_secure_cmd_classes,
            "created_date": self._created_date,
            "smart_energy_optimizer": self._smart_energy_optimizer,
            "linked_security_zone: ": self._linked_security_zone,
        }
