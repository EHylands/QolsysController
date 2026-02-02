import logging
from typing import TYPE_CHECKING

from qolsys_controller.protocol_zwave.device import QolsysZWaveDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysLock(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", lock_dict: dict[str, str], zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)

        self._lock_id: str = lock_dict.get("_id", "")
        self._lock_partition_id: str = lock_dict.get("partition_id", "")
        self._lock_name: str = lock_dict.get("doorlock_name", "")
        self._lock_status: str = lock_dict.get("status", "")
        self._lock_node_id: str = lock_dict.get("node_id", "")
        self._lock_created_by: str = lock_dict.get("created_by", "")
        self._lock_created_date: str = lock_dict.get("created_date", "")
        self._lock_updated_by: str = lock_dict.get("updated_by", "")
        self._lock_last_updated_date: str = lock_dict.get("last_updated_date", "")
        self._lock_remote_arming: str = lock_dict.get("remote_arming", "")
        self._lock_keyfob_arming: str = lock_dict.get("keyfob_arming", "")
        self._lock_panel_arming: str = lock_dict.get("panel_arming", "")
        self._lock_endpoint: str = lock_dict.get("endpoint", "")
        self._lock_paired_status: str = lock_dict.get("paired_status", "")

    def is_locked(self) -> bool:
        return self.lock_status.lower() == "locked"

    async def lock(self) -> None:
        await self._controller.command_zwave_doorlock_set(self.node_id, "0", True)

    async def unlock(self) -> None:
        await self._controller.command_zwave_doorlock_set(self.node_id, "0", False)

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def lock_node_id(self) -> str:
        return self._lock_node_id

    @property
    def lock_status(self) -> str:
        return self._lock_status

    @lock_status.setter
    def lock_status(self, value: str) -> None:
        if self._lock_status != value:
            LOGGER.debug("Lock%s (%s) - status: %s", self.node_id, self.lock_name, value)
            self._lock_status = value
            self.notify()

    @property
    def lock_name(self) -> str:
        return self._lock_name

    @lock_name.setter
    def lock_name(self, value: str) -> None:
        if self._lock_name != value:
            LOGGER.debug("Lock%s (%s) - name: %s", self.node_id, self.lock_name, value)
            self._lock_name = value
            self.notify()

    @property
    def paired_status(self) -> str:
        return self._paired_status

    @paired_status.setter
    def paired_status(self, value: str) -> None:
        if self._paired_status != value:
            LOGGER.debug("Lock%s (%s) - paired_status: %s", self.node_id, self.lock_name, value)
            self._lock_paired_status = value
            self.notify()

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        super().update_raw(payload, endpoint)

    def update_lock(self, data: dict[str, str]) -> None:  # noqa: PLR0912
        # Check if we are updating same zoneid
        node_id_update = data.get("node_id", "")
        if node_id_update != self.lock_node_id:
            LOGGER.error(
                "Updating Lock %s (%s) with Lock '%s' (different id)", self.lock_node_id, self.lock_name, node_id_update
            )
            return

        self.start_batch_update()

        if "partition_id" in data:
            self._lock_partition_id = data.get("partition_id", "")
        if "lock_name" in data:
            self.lock_name = data.get("lock_name", "")
        if "status" in data:
            self.lock_status = data.get("status", "")
        if "created_by" in data:
            self._lock_created_by = data.get("created_by", "")
        if "created_date" in data:
            self._lock_created_date = data.get("created_date", "")
        if "updated_by" in data:
            self._lock_updated_by = data.get("updated_by", "")
        if "last_updated_date" in data:
            self._lock_last_updated_date = data.get("last_updated_date", "")
        if "remote_arming" in data:
            self._lock_remote_arming = data.get("remote_arming", "")
        if "keyfob_arming" in data:
            self._lock_keyfob_arming = data.get("keyfob_arming", "")
        if "panel_arming" in data:
            self._lock_panel_arming = data.get("panel_arming", "")
        if "endpoint" in data:
            self._lock_endpoint = data.get("endpoint", "")
        if "paired_status" in data:
            self._lock_paired_status = data.get("paired_status", "")

        self.end_batch_update()

    def to_dict_lock(self) -> dict[str, str]:
        return {
            "_id": self._lock_id,
            "partition_id": self._lock_partition_id,
            "doorlock_name": self.lock_name,
            "node_id": self.lock_node_id,
            "status": self.lock_status,
            "created_by": self._lock_created_by,
            "created_date": self._lock_created_date,
            "updated_by": self._lock_updated_by,
            "last_updated_date": self._lock_last_updated_date,
            "remote_arming": self._lock_remote_arming,
            "keyfob_arming": self._lock_keyfob_arming,
            "panel_arming": self._lock_panel_arming,
            "endpoint": self._lock_endpoint,
            "paired_status": self._lock_paired_status,
        }
