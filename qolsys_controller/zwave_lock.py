import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysLock(QolsysZWaveDevice):

    LOCK_STATUS_ARRAY = ["Locked"]  # noqa: RUF012

    def __init__(self,lock_dict:dict,zwave_dict:dict) -> None:

        super().__init__(zwave_dict)

        self._lock_id = lock_dict.get("_id")
        self._lock_version =  lock_dict.get("version","")
        self._lock_opr = lock_dict.get("opr","")
        self._lock_partition_id = lock_dict.get("partition_id","")
        self._lock_name = lock_dict.get("doorlock_name","")
        self._lock_status = lock_dict.get("status","")
        self._lock_node_id = lock_dict.get("node_id","")
        self._lock_created_by = lock_dict.get("created_by","")
        self._lock_created_date = lock_dict.get("created_date","")
        self._lock_updated_by = lock_dict.get("updated_by","")
        self._lock_last_updated_date = lock_dict.get("last_updated_date","")
        self._lock_remote_arming = lock_dict.get("remote_arming","")
        self._lock_keyfob_arming = lock_dict.get("keyfob_arming","")
        self._lock_panel_arming = lock_dict.get("panel_arming","")
        self._lock_endpoint = lock_dict.get("endpoint","")
        self._lock_paired_status = lock_dict.get("paired_status","")

    @property
    def lock_node_id(self) -> str:
        return self._lock_node_id

    @property
    def lock_status(self) -> str:
        return self._lock_status

    @property
    def lock_name(self) -> str:
        return self._lock_name

    @property
    def paired_status(self) -> str:
        return self._paired_status

    @lock_status.setter
    def lock_status(self,value:str) -> None:
        if self._lock_status != value:
            LOGGER.debug("Lock%s (%s) - status: %s",self.node_id,self.lock_name,value)
            self._lock_status = value
            self.notify()

    @lock_name.setter
    def lock_name(self,value:str) -> None:
        if self._lock_name != value:
            LOGGER.debug("Lock%s (%s) - name: %s",self.node_id,self.lock_name,value)
            self._lock_name = value
            self.notify()

    @paired_status.setter
    def paired_status(self, value:str) -> None:
        if self._paired_status != value:
            LOGGER.debug("Lock%s (%s) - paired_status: %s",self.node_id,self.lock_name,value)
            self._lock_paired_status = value
            self.notify()

    def update_lock(self,data:dict) -> None:  # noqa: C901, PLR0912
        # Check if we are updating same zoneid
        node_id_update = data.get("node_id","")
        if node_id_update != self.lock_node_id:
            LOGGER.error("Updating Lock %s (%s) with Lock '%s' (different id)",self.lock_node_id,self.lock_name,node_id_update)
            return

        self.start_batch_update()

        if "version" in  data:
            self._lock_version = data.get("version")
        if "opr" in data:
            self._lock_opr = data.get("opr")
        if "partition_id" in data:
            self._lock_partition_id = data.get("partition_id")
        if "lock_name" in data:
            self.lock_name = data.get("lock_name")
        if "status" in data:
            self.lock_status = data.get("status")
        if "created_by" in data:
            self._lock_created_by = data.get("created_by")
        if "created_date" in data:
            self._lock_created_date = data.get("created_date")
        if "updated_by" in data:
            self._lock_updated_by = data.get("updated_by")
        if "last_updated_date" in data:
            self._lock_last_updated_date = data.get("last_updated_date")
        if "remote_arming" in data:
            self._lock_remote_arming = data.get("remote_arming")
        if "keyfob_arming" in data:
            self._lock_keyfob_arming = data.get("keyfob_arming")
        if "panel_arming" in data:
            self._lock_panel_arming = data.get("panel_arming")
        if "endpoint" in data:
            self._lock_endpoint = data.get("endpoint")
        if "paired_status" in data:
            self._lock_paired_status = data.get("paired_status")

        self.end_batch_update()

    def to_dict_dimmer(self) -> dict:
        return {
            "_id": self._lock_id,
            "version": self._lock_version,
            "opr": self._lock_opr,
            "partition_id": self._lock_partition_id,
            "doorlock_name": self.lock_name,
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




