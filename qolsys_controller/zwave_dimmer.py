import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysDimmer(QolsysZWaveDevice):

    def __init__(self,dimmer_dict:dict,zwave_dict:dict) -> None:

        super().__init__(zwave_dict)

        self._dimmer_id = dimmer_dict.get("_id")
        self._dimmer_version =  dimmer_dict.get("version","")
        self._dimmer_opr = dimmer_dict.get("opr","")
        self._dimmer_partition_id = dimmer_dict.get("partition_id","")
        self._dimmer_name = dimmer_dict.get("dimmer_name","")
        self._dimmer_status = dimmer_dict.get("status","")
        self._dimmer_level = dimmer_dict.get("level","")
        self._dimmer_node_id = dimmer_dict.get("node_id","")
        self._dimmer_created_by = dimmer_dict.get("created_by","")
        self._dimmer_created_date = dimmer_dict.get("created_date","")
        self._dimmer_updated_by = dimmer_dict.get("updated_by","")
        self._dimmer_last_updated_date = dimmer_dict.get("last_updated_date","")
        self._dimmer_endpoint = dimmer_dict.get("endpoint","")
        self._dimmer_power_details = dimmer_dict.get("power_details","")
        self._dimmer_paired_status = dimmer_dict.get("paired_status","")

    @property
    def dimmer_node_id(self) -> str:
        return self._dimmer_node_id

    @property
    def dimmer_status(self) -> str:
        return self._dimmer_status

    @property
    def dimmer_name(self) -> str:
        return self._dimmer_name

    @property
    def dimmer_level(self) -> str:
        return self._dimmer_level

    @dimmer_level.setter
    def dimmer_level(self,value:str) -> None:
        if self._dimmer_level != value:
            LOGGER.debug("Dimmer%s (%s) - level: %s",self.node_id,self.dimmer_name,value)
            self._dimmer_level = value
            self.notify()

    @dimmer_status.setter
    def dimmer_status(self,value:str) -> None:
        if self._dimmer_status != value:
            LOGGER.debug("Dimmer%s (%s) - status: %s",self.node_id,self.dimmer_name,value)
            self._dimmer_status = value
            self.notify()

    @dimmer_name.setter
    def dimmer_name(self,value:str) -> None:
        if self._dimmer_name != value:
            LOGGER.debug("Dimmer%s (%s) - name: %s",self.node_id,self.dimmer_name,value)
            self._dimmer_name = value
            self.notify()

    def is_on(self) -> bool:
        return self.dimmer_status == "On"

    def update_dimmer(self,content_values:dict) -> None:  # noqa: C901
        # Check if we are updating same none_id
        node_id_update = content_values.get("node_id","")
        if node_id_update != self._dimmer_node_id:
            LOGGER.error("Updating Dimmer %s (%s) with dimmer %s (different id)",self._node_id,self.dimmer_name,node_id_update)
            return

        self.start_batch_update()

        if "status" in content_values:
            self.dimmer_status = content_values.get("status")
        if "level" in content_values:
            self.dimmer_level = content_values.get("level")
        if "dimmer_name" in content_values:
            self.dimmer_name = content_values.get("dimmer_name")
        if "created_by" in content_values:
            self._dimmer_created_by = content_values.get("created_by")
        if "created_date" in content_values:
            self._dimmer_created_date = content_values.get("created_date")
        if "version" in  content_values:
            self._dimmer_version = content_values.get("version")
        if "opr" in content_values:
            self._dimmer_opr = content_values.get("opr")
        if "partition_id" in content_values:
            self.partition_id = content_values.get("partition_id")
        if "updated_by" in content_values:
            self._dimmer_updated_by = content_values.get("updated_by")
        if "last_updated_date" in content_values:
            self._last_updated_date= content_values.get("last_updated_date")
        if "endpoint" in content_values:
            self._dimmer_endpoint = content_values.get("endpoint")
        if "power_details" in content_values:
            self._dimmer_power_details = content_values.get("power_details")
        if "paired_status" in content_values:
            self._dimmer_paired_status = content_values.get("paired_status")

        self.end_batch_update()

    def to_dict_dimmer(self) -> dict:
        return {
            "_id": self._dimmer_id,
            "version": self._dimmer_version,
            "opr": self._dimmer_opr,
            "partition_id": self._partition_id,
            "dimmer_name": self.dimmer_name,
            "status": self.dimmer_status,
            "level": self.dimmer_level,
            "node_id": self.dimmer_node_id,
            "created_by": self._dimmer_created_by,
            "created_date": self._dimmer_created_date,
            "updated_by": self._dimmer_updated_by,
            "last_updated_date": self._last_updated_date,
            "endpoint": self._dimmer_endpoint,
            "power_details": self._dimmer_power_details,
            "paired_status": self._dimmer_paired_status,
        }
