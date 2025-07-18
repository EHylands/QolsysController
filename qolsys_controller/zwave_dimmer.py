import logging

from qolsys_controller.zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysDimmer(QolsysZWaveDevice):

    NOTIFY_UPDATE_DIMMER_LEVEL = 'update_dimmer_level'
    NOTIFY_UPDATE_DIMMER_STATUS = 'update_dimmer_status'
    NOTIFY_UPDATE_DIMMER_NAME = 'update_dimmer_name'

    def __init__(self,dimmer_dict,zwave_dict) -> None:
                                      
        super().__init__(zwave_dict)

        self._dimmer_id = dimmer_dict.get('_id')
        self._dimmer_version =  dimmer_dict.get('version')
        self._dimmer_opr = dimmer_dict.get('opr')
        self._dimmer_partition_id = dimmer_dict.get('partition_id')
        self._dimmer_name = dimmer_dict.get('dimmer_name')
        self._dimmer_status = dimmer_dict.get('status')
        self._dimmer_level = dimmer_dict.get('level')
        self._dimmer_node_id = dimmer_dict.get('node_id')
        self._dimmer_created_by = dimmer_dict.get('created_by')
        self._dimmer_created_date = dimmer_dict.get('created_date')
        self._dimmer_updated_by = dimmer_dict.get('updated_by')
        self._dimmer_last_updated_date = dimmer_dict.get('last_updated_date')
        self._dimmer_endpoint = dimmer_dict.get('endpoint')
        self._dimmer_power_details = dimmer_dict.get('power_details')
        self._dimmer_paired_status = dimmer_dict.get('paired_status')

    @property
    def dimmer_node_id(self):
        return self._dimmer_node_id
    
    @property
    def dimmer_status(self):
        return self._dimmer_status
    
    @property
    def dimmer_name(self):
        return self._dimmer_name

    @property 
    def dimmer_level(self):
        return self._dimmer_level
    
    @dimmer_level.setter
    def dimmer_level(self,value):
        if self._dimmer_level != value:
            LOGGER.debug(f"Dimmer{self._node_id} ({self.dimmer_name}) - level: {value}")
            prev_value = self._dimmer_level
            self._dimmer_level = value
            self.notify(change=self.NOTIFY_UPDATE_DIMMER_LEVEL,node_id=self._node_id, prev_value=prev_value, new_value=value)

    @dimmer_status.setter
    def dimmer_status(self,value):
        if self._dimmer_status != value:
            LOGGER.debug(f"Dimmer{self._node_id} ({self.dimmer_name}) - status: {value}")
            prev_value = self._dimmer_status
            self._dimmer_status = value
            self.notify(change=self.NOTIFY_UPDATE_DIMMER_STATUS,node_id=self._node_id, prev_value=prev_value, new_value=value)
    
    @dimmer_name.setter
    def dimmer_name(self,value):
        if self._dimmer_name != value:
            LOGGER.debug(f"Dimmer{self._node_id} ({self.dimmer_name}) - name: {value}")
            prev_value = self._dimmer_name
            self._dimmer_name = value
            self.notify(change=self.NOTIFY_UPDATE_DIMMER_NAME,node_id=self._node_id, prev_value=prev_value, new_value=value)

    def update(self,content_values:dict):
          # Check if we are updating same zoneid        
        node_id_update = content_values.get('node_id','')
        if node_id_update != self._node_id:
            LOGGER.error(f"Updating Dimmer '{self._node_id}' ({self.dimmer_name}) with dimmer '{node_id_update}' (different id)")
            return
        
        # Update status
        if 'status' in content_values:
            self.dimmer_status = content_values.get('status')

        # Update level
        if 'level' in content_values:
            self.dimmer_level = content_values.get('level')

        # Update dimmer_name
        if 'dimmer_name' in content_values:
            self.dimmer_name = content_values.get('dimmer_name')

