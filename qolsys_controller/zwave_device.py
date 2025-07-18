from qolsys_controller.observable import QolsysObservable

class QolsysZWaveDevice(QolsysObservable):

    def __init__(self,zwave_dict:dict):
        super().__init__()

        self._id = zwave_dict.get('_id')
        self._node_id = zwave_dict.get('node_id','')
        self._node_name = zwave_dict.get('node_name','')
        self._node_type =  zwave_dict.get('node_type','')
        self._node_status = zwave_dict.get('node_status','')
        self._partition_id = zwave_dict.get('partition_id','')
        self._node_secure_cmd_cls = zwave_dict.get('node_secure_cmd_cls','')
        self._node_battery_level = zwave_dict.get('node_battery_level','')
        self._node_battery_level_value = zwave_dict.get('node_battery_level_value','')
        self._is_node_listening_node = zwave_dict.get('is_node_listening_node','')
        self._basic_report_value = zwave_dict.get('basic_report_value','')
        self._switch_multilevel_report_value = zwave_dict.get('switch_multilevel_report_value','')
        self._basic_device_type = zwave_dict.get('basic_device_type','')
        self._generic_device_type = zwave_dict.get('generic_device_type','')
        self._specific_device_type = zwave_dict.get('specific_device_type','') 
        self._num_secure_command_class = zwave_dict.get('num_secure_command_class','')
        self._secure_command_class = zwave_dict.get('secure_command_class','')
        self._manufacture_id = zwave_dict.get('manufacture_id','')
        self._product_type = zwave_dict.get('product_type','')
        self._device_protocol = zwave_dict.get('device_protocol','')
        self._paired_status = zwave_dict.get('paired_status','') 
        self._is_device_sleeping = zwave_dict.get('is_device_sleeping','') 
        self._is_device_hidden = zwave_dict.get('is_device_hidden','') 
        self._last_updated_date = zwave_dict.get('last_updated_date','') 
        self._command_class_list = zwave_dict.get('command_class_list','') 

        @property 
        def node_id(self):
            return self._node_id
        
        @node_id.setter
        def node_id(self,value):
            self._node_id = value


    