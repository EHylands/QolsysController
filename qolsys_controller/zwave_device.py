import logging

from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysZWaveDevice(QolsysObservable):

    def __init__(self,zwave_dict:dict) -> None:
        super().__init__()

        self._id = zwave_dict.get("_id")
        self._node_id = zwave_dict.get("node_id","")
        self._node_name = zwave_dict.get("node_name","")
        self._node_type =  zwave_dict.get("node_type","")
        self._node_status = zwave_dict.get("node_status","")
        self._partition_id = zwave_dict.get("partition_id","")
        self._node_secure_cmd_cls = zwave_dict.get("node_secure_cmd_cls","")
        self._node_battery_level = zwave_dict.get("node_battery_level","")
        self._node_battery_level_value = zwave_dict.get("node_battery_level_value","")
        self._is_node_listening_node = zwave_dict.get("is_node_listening_node","")
        self._basic_report_value = zwave_dict.get("basic_report_value","")
        self._switch_multilevel_report_value = zwave_dict.get("switch_multilevel_report_value","")
        self._basic_device_type = zwave_dict.get("basic_device_type","")
        self._generic_device_type = zwave_dict.get("generic_device_type","")
        self._specific_device_type = zwave_dict.get("specific_device_type","")
        self._num_secure_command_class = zwave_dict.get("num_secure_command_class","")
        self._secure_command_class = zwave_dict.get("secure_command_class","")
        self._manufacture_id = zwave_dict.get("manufacture_id","")
        self._product_type = zwave_dict.get("product_type","")
        self._device_protocol = zwave_dict.get("device_protocol","")
        self._paired_status = zwave_dict.get("paired_status","")
        self._is_device_sleeping = zwave_dict.get("is_device_sleeping","")
        self._is_device_hidden = zwave_dict.get("is_device_hidden","")
        self._last_updated_date = zwave_dict.get("last_updated_date","")
        self._command_class_list = zwave_dict.get("command_class_list","")

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def paired_status(self) -> str:
        return self._paired_status

    @property
    def node_battery_level(self) -> str:
        return self._node_battery_level

    @property
    def node_battery_level_value(self) -> str:
        return self._node_battery_level_value

    @property
    def node_status(self) -> str:
        return self._node_status

    @property
    def node_name(self) -> str:
        return self._node_name

    @property
    def node_type(self) -> str:
        return self._node_type

    @property
    def partition_id(self) -> str:
        return self._partition_id

    def update_base(self,data:dict) -> None:  # noqa: C901, PLR0912, PLR0915

        # Check if we are updating same node_id
        node_id_update = data.get("node_id","")
        if node_id_update != self._node_id:
            LOGGER.error("Updating ZWave%s (%s) with ZWave%s (different node_id)",self.node_id,self.node_name,node_id_update)
            return

        self.start_batch_update()

        if "paired_status" in data:
            self.paired_status = data.get("paired_status")
        if "node_battery_level" in data:
            self.node_battery_level = data.get("node_battery_level")
        if "node_battery_level_value" in data:
            self.node_battery_level_value = data.get("node_battery_level_value")
        if "node_status" in data:
            self.node_status = data.get("node_status")
        if "node_name" in data:
            self.node_name = data.get("node_name")
        if "node_type" in data:
            self.node_type = data.get("node_type")
        if "partition_id" in data:
            self.partition_id = data.get("partition_id")
        if "node_secure_cmd_cls" in data:
            self._node_secure_cmd_cls = data.get("node_secure_cmd_cls")
        if "is_node_listening_node" in data:
            self._is_node_listening_node = data.get("is_node_listening_node")
        if "basic_report_value" in data:
            self._basic_report_value = data.get("basic_report_value")
        if "switch_multilevel_report_value" in data:
            self._switch_multilevel_report_value = data.get("switch_multilevel_report_value")
        if "basic_device_type" in data:
            self._basic_device_type = data.get("basic_device_type")
        if "generic_device_type" in data:
            self._generic_device_type = data.get("generic_device_type")
        if "specific_device_type" in data:
            self._specific_device_type = data.get("specific_device_type")
        if "num_secure_command_class" in data:
            self._num_secure_command_class = data.get("num_secure_command_class")
        if "secure_command_class" in data:
            self._secure_command_class = data.get("secure_command_class")
        if "manufacture_id" in data:
            self._manufacture_id = data.get("manufacture_id")
        if "product_type" in data:
            self._product_type = data.get("product_type")
        if "device_protocol" in data:
            self._device_protocol = data.get("device_protocol")
        if "paired_status" in data:
            self.paired_status = data.get("paired_status")
        if "is_device_sleeping" in data:
            self._is_device_sleeping = data.get("is_device_sleeping")
        if "is_device_hidden" in data:
            self._is_device_hidden = data.get("is_device_hidden")
        if "last_updated_date" in data:
            self._last_updated_date = data.get("last_updated_date")
        if "command_class_list" in data:
            self._last_updated_date = data.get("command_class_list")

        self.end_batch_update()

    @node_id.setter
    def node_id(self,value:str) -> str:
        self._node_id = value

    @paired_status.setter
    def paired_status(self,value:str) -> str:
        if self._paired_status != value:
            LOGGER.debug("ZWave%s (%s) - paired_status: %s",self.node_id,self.node_name,value)
            self._paired_status = value
            self.notify()

    @node_battery_level.setter
    def node_battery_level(self,value:str) -> None:
        if self._node_battery_level != value:
            LOGGER.debug("ZWave%s (%s) - node_battery_level: %s",self.node_id,self.node_name,value)
            self._node_battery_level = value
            self.notify()

    @node_battery_level_value.setter
    def node_battery_level_value(self,value:str) -> str:
        if self._node_battery_level_value != value:
            LOGGER.debug("ZWave%s (%s) - node_battery_level_value: %s",self.node_id,self.node_name,value)
            self._node_battery_level_value = value
            self.notify()

    @node_status.setter
    def node_status(self,value:str) -> str:
        if self._node_status != value:
            LOGGER.debug("ZWave%s (%s) - node_status: %s",self.node_id,self.node_name,value)
            self._node_status = value
            self.notify()

    @node_name.setter
    def node_name(self,value:str) -> str:
        if self._node_name != value:
            LOGGER.debug("ZWave%s (%s) - node_name: %s",self.node_id,self.node_name,value)
            self._node_name = value
            self.notify()

    @node_type.setter
    def node_type(self,value:str) -> str:
        if self._node_type != value:
            LOGGER.debug("ZWave%s (%s) - node_type: %s",self.node_id,self.node_name,value)
            self._node_type = value
            self.notify()

    @partition_id.setter
    def partition_id(self,value:str) -> str:
        if self._partition_id != value:
            LOGGER.debug("ZWave%s (%s) - partition_id: %s",self._node_id,self._node_name,value)
            self._partition_id = value
            self.notify()

    def to_dict_base(self) -> dict:
        return {
            "_id": self._id,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "node_status": self.node_status,
            "partition_id": self._partition_id,
            "node_battery_level": self.node_battery_level,
            "node_battery_level_value": self.node_battery_level_value,
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
        }
