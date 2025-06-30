from qolsys.observable import QolsysObservable

class QolsysZWaveDevice(QolsysObservable):

    def __init__(self,
                 id:int,
                 node_id:int,
                 node_name:str,
                 node_type:str,
                 node_status:str,
                 partition_id:int,
                 node_secure_cmd_cls:str,
                 node_battery_level:str,
                 node_battery_level_value:str,
                 is_node_listening_node:str,
                 basic_report_value:str,
                 switch_multilevel_report_value:str,
                 basic_device_type:int,
                 generic_device_type:int,
                 specific_device_type:int,
                 num_secure_command_class:str,
                 secure_command_class: str,
                 manufacture_id:str,
                 product_type:str,
                 device_protocol:str,
                 paired_status:str,
                 is_device_sleeping:str,
                 is_device_hidden:str,
                 last_updated_date:str,
                 command_class_list:list

                    ):
        super().__init__()

        self._id = id
        self._node_id = node_id
        self._node_name = node_name
        self._node_type = node_type
        self._node_status = node_status
        self._partition_id = partition_id
        self._node_secure_cmd_cls = node_secure_cmd_cls
        self._node_battery_level = node_battery_level
        self._node_battery_level_value = node_battery_level_value
        self._is_node_listening_node = is_node_listening_node
        self._basic_report_value = basic_report_value
        self._switch_multilevel_report_value = switch_multilevel_report_value
        self._basic_device_type = basic_device_type
        self._generic_device_type = generic_device_type
        self._specific_device_type = specific_device_type
        self._num_secure_command_class = num_secure_command_class
        self._secure_command_class = secure_command_class
        self._manufacture_id = manufacture_id
        self._product_type = product_type
        self._device_protocol = device_protocol
        self._paired_status = paired_status
        self._is_device_sleeping = is_device_sleeping
        self._is_device_hidden = is_device_hidden
        self._last_updated_date = last_updated_date
        self._command_class_list = command_class_list


    