import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysThermostat(QolsysZWaveDevice):

    def __init__(self,thermostat_dict:dict,zwave_dict:dict)-> None:

        super().__init__(zwave_dict)

        self._thermostat_id = thermostat_dict.get("_id")
        self._thermostat_version =  thermostat_dict.get("version","")
        self._thermostat_opr = thermostat_dict.get("opr","")
        self._thermostat_partition_id = thermostat_dict.get("partition_id","")
        self._thermostat_name = thermostat_dict.get("thermostat_name","")
        self._thermostat_node_id = thermostat_dict.get("node_id","")
        self._thermostat_device_temp_unit = thermostat_dict.get("device_temp_unit","") # 'F'
        self._thermostat_current_temp = thermostat_dict.get("current_temp","") # "78.0"
        self._thermostat_target_cool_temp = thermostat_dict.get("target_cool_temp","") # "78"
        self._thermostat_target_heat_temp = thermostat_dict.get("target_heat_temp","") # "65"
        self._thermostat_target_temp = thermostat_dict.get("target_temp","")
        self._thermostat_power_usage = thermostat_dict.get("power_usage","")
        self._thermostat_mode = thermostat_dict.get("thermostat_mode","") #"2"
        self._thermostat_mode_bitmask = thermostat_dict.get("thermostat_mode_bitmask","") # "7,24"
        self._thermostat_fan_mode = thermostat_dict.get("fan_mode","") # "0"
        self._thermostat_fan_mode_bitmask = thermostat_dict.get("fan_mode_bitmask","") # "67"
        self._thermostat_set_point_mode = thermostat_dict.get("set_point_mode","")
        self._thermostat_set_point_mode_bitmask = thermostat_dict.get("set_point_mode_bitmask","") # "-122,1"
        self._thermostat_created_by = thermostat_dict.get("created_by","")
        self._thermostat_created_date = thermostat_dict.get("created_date","")
        self._thermostat_updated_by = thermostat_dict.get("updated_by","")
        self._thermostat_last_updated_date = thermostat_dict.get("last_updated_date","")
        self._thermostat_mode_updated_time = thermostat_dict.get("thermostat_mode_updated_time","")
        self._thermostat_fan_mode_updated_time = thermostat_dict.get("fan_mode_updated_time","")
        self._thermostat_set_point_mode_updated_time = thermostat_dict.get("set_point_mode_updated_time","")
        self._thermostat_target_cool_temp_updated_time = thermostat_dict.get("target_cool_temp_updated_time","")
        self._thermostat_target_heat_temp_updated_time = thermostat_dict.get("target_heat_temp_updated_time","")
        self._thermostat_current_temp_updated_time = thermostat_dict.get("current_temp_updated_time","")
        self._thermostat_endpoint = thermostat_dict.get("endpoint","")
        self._thermostat_paired_status = thermostat_dict.get("paired_status","")
        self._thermostat_configuration_parameter = thermostat_dict.get("configuration_parameter","")

    @property
    def thermostat_node_id(self) -> str:
        return self._thermostat_node_id

    @property
    def thermostat_name(self) -> str:
        return self._thermostat_name

    @property
    def thermostat_device_temp_unit(self) -> str:
        return self._thermostat_device_temp_unit

    @property
    def thermostat_current_temp(self) -> str:
        return self._thermostat_current_temp

    @property
    def thermostat_target_cool_temp(self) -> str:
        return self._thermostat_target_cool_temp

    @property
    def thermostat_target_heat_temp(self) -> str:
        return self._thermostat_target_heat_temp

    @property
    def thermostat_target_temp(self) -> str:
        return self._thermostat_target_temp

    @property
    def thermostat_mode(self) -> str:
        return self._thermostat_mode

    @property
    def thermostat_fan_mode(self) -> str:
        return self.thermostat_fan_mode

    @property
    def thermostat_set_point_mode(self) -> str:
        return self._thermostat_set_point_mode

    @thermostat_name.setter
    def thermostat_name(self,value:str) -> None:
        if self._thermostat_name != value:
            LOGGER.debug("Thermostat%s (%s) - name: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_name = value
            self.notify()

    @thermostat_device_temp_unit.setter
    def thermostat_device_temp_unit(self,value:str) -> None:
        if self._thermostat_device_temp_unit != value:
            LOGGER.debug("Thermostat%s (%s) - device_temp_unit: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_device_temp_unit = value
            self.notify()

    @thermostat_current_temp.setter
    def thermostat_current_temp(self,value:str) -> None:
        if self._thermostat_current_temp != value:
            LOGGER.debug("Thermostat%s (%s) - current_temp: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_current_temp = value
            self.notify()

    @thermostat_target_cool_temp.setter
    def thermostat_target_cool_temp(self,value:str) -> None:
        if self._thermostat_target_cool_temp != value:
            LOGGER.debug("Thermostat%s (%s) - target_cool_temp: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_target_cool_temp = value
            self.notify()

    @thermostat_target_heat_temp.setter
    def thermostat_target_heat_temp(self,value:str) -> None:
        if self._thermostat_target_heat_temp != value:
            LOGGER.debug("Thermostat%s (%s) - target_heat_temp: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_target_heat_temp = value
            self.notify()

    @thermostat_target_temp.setter
    def thermostat_target_temp(self,value:str) -> None:
        if self._thermostat_target_temp != value:
            LOGGER.debug("Thermostat%s (%s) - target_temp: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_target_temp = value
            self.notify()

    @thermostat_mode.setter
    def thermostat_mode(self,value:str) -> None:
        if self._thermostat_mode != value:
            LOGGER.debug("Thermostat%s (%s) - mode: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_mode = value
            self.notify()

    @thermostat_fan_mode.setter
    def thermostat_fan_mode(self,value:str) -> None:
        if self._thermostat_fan_mode != value:
            LOGGER.debug("Thermostat%s (%s) - fan_mode: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_fan_mode = value
            self.notify()

    @thermostat_set_point_mode.setter
    def thermostat_set_point_mode(self,value:str) -> None:
        if self._thermostat_set_point_mode != value:
            LOGGER.debug("Thermostat%s (%s) - set_point_mode: %s",self.thermostat_node_id,self.thermostat_name,value)
            self._thermostat_set_point_mode = value
            self.notify()

    def update_thermostat(self,data:dict) -> None:  # noqa: C901, PLR0912, PLR0915
        # Check if we are updating same none_id
        node_id_update = data.get("node_id","")
        if node_id_update != self.thermostat_node_id_node_id:
            LOGGER.error("Updating Thermostat '%s' (%s) with Thermostat '%s' (different id)",self.thermostat_node_id,self.thermostat_name,node_id_update)
            return

        self.start_batch_update()

        if "version" in  data:
            self._thermostat_version = data.get("version")
        if "opr" in data:
            self._thermostat_opr = data.get("opr")
        if "partition_id" in data:
            self._thermostat_partition_id = data.get("partition_id")
        if "thermostat_name" in data:
            self.thermostat_name = data.get("thermostat_name")
        if "device_temp_unit" in data:
            self.thermostat_device_temp_unit = data.get("device_temp_unit")
        if "current_temp" in data:
            self.thermostat_current_temp = data.get("current_temp")
        if "target_cool_temp" in data:
            self.thermostat_target_cool_temp = data.get("target_cool_temp")
        if "target_heat_temp" in data:
            self.thermostat_target_heat_temp = data.get("target_heat_temp")
        if "target_temp" in data:
            self.thermostat_target_temp = data.get("target_temp")
        if "power_usage" in data:
            self._thermostat_power_usage = data.get("power_usage")
        if "thermostat_mode" in data:
            self.thermostat_mode = data.get("thermostat_mode")
        if "thermostat_mode_bitmask" in data:
            self._thermostat_mode_bitmask = data.get("thermostat_mode_bitmask")
        if "fan_mode" in data:
            self.thermostat_fan_mode = data.get("fan_mode")
        if "fan_mode_bitmask" in data:
            self._thermostat_fan_mode_bitmask = data.get("fan_mode_bitmask")
        if "set_point_mode" in data:
            self.thermostat_set_point_mode = data.get("set_point_mode")
        if "set_point_mode_bitmask" in data:
            self._thermostat_set_point_mode_bitmask = data.get("set_point_mode_bitmask")
        if "created_by" in data:
            self._thermostat_created_by = data.get("created_by")
        if "updated_by" in data:
            self._thermostat_updated_by = data.get("updated_by")
        if "last_updated_date" in data:
            self._thermostat_last_updated_date = data.get("last_updated_date")
        if "thermostat_mode_updated_time" in data:
            self._thermostat_mode_updated_time = data.get("thermostat_mode_updated_time")
        if "fan_mode_updated_time" in data:
            self._thermostat_fan_mode_updated_time = data.get("fan_mode_updated_time")
        if "set_point_mode_updated_time" in data:
            self._thermostat_set_point_mode_updated_time = data.get("set_point_mode_updated_time")
        if "target_cool_temp_updated_time" in data:
            self._thermostat_target_cool_temp_updated_time = data.get("target_cool_temp_updated_time")
        if "target_heat_temp_updated_time" in data:
            self._thermostat_target_heat_temp_updated_time = data.get("target_heat_temp_updated_time")
        if "current_temp_updated_time" in data:
            self._thermostat_current_temp_updated_time= data.get("current_temp_updated_time")
        if "paired_status" in data:
            self._thermostat_paired_status = data.get("paired_status")
        if "endpoint" in data:
            self._thermostat_endpoint = data.get("endpoint")
        if "configuration_parameter" in data:
            self._thermostat_configuration_parameter = data.get("configuration_parameter")

        self.end_batch_update()

    def to_dict_thermostat(self) -> dict:
        return {
            "_id": self._thermostat_id,
            "version": self._thermostat_version,
            "opr": self._thermostat_opr,
            "partition_id": self._thermostat_partition_id,
            "thermostat_name": self.thermostat_name,
            "device_temp_unit": self.thermostat_device_temp_unit,
            "current_temp": self.thermostat_current_temp,
            "target_cool_temp": self.thermostat_target_cool_temp,
            "target_heat_temp": self.thermostat_target_heat_temp,
            "target_temp": self.thermostat_target_temp,
            "power_usage": self._thermostat_power_usage,
            "thermostat_mode": self.thermostat_mode,
            "thermostat_mode_bitmask": self._thermostat_mode_bitmask,
            "fan_mode": self.thermostat_fan_mode,
            "fan_mode_bitmask": self._thermostat_fan_mode_bitmask,
            "set_point_mode": self.thermostat_set_point_mode,
            "set_point_mode_bitmask": self._thermostat_set_point_mode_bitmask,
            "created_by": self._thermostat_created_by,
            "updated_by": self._thermostat_updated_by,
            "last_updated_date": self._thermostat_last_updated_date,
            "thermostat_mode_updated_time": self._thermostat_mode_updated_time,
            "fan_mode_updated_time": self._thermostat_fan_mode_updated_time,
            "set_point_mode_updated_time": self._thermostat_set_point_mode_updated_time,
            "target_cool_temp_updated_time": self._thermostat_target_cool_temp_updated_time,
            "target_heat_temp_updated_time": self._thermostat_target_heat_temp_updated_time,
            "current_temp_updated_time": self._thermostat_current_temp_updated_time,
            "paired_status": self._thermostat_paired_status,
            "endpoint": self._thermostat_endpoint,
            "configuration_parameter": self._thermostat_configuration_parameter,
        }

