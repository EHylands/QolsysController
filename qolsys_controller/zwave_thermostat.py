import logging

from qolsys_controller.zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysThermostat(QolsysZWaveDevice):

#_id":"1","version":"0","opr":"0","partition_id":"0","thermostat_id":"4","thermostat_name":"Thermostat","current_temp":"78.0","target_cool_temp":"78","target_heat_temp":"65","target_temp":"25","power_usage":"0","thermostat_mode":"2","thermostat_mode_bitmask":"7,24","fan_mode":"0","fan_mode_bitmask":"67","set_point_mode":"0","set_point_mode_bitmask":"-122,1","node_id":"4","created_by":"created_by","created_date":"6643256461","updated_by":"updated_by","last_updated_date":"41734801611","thermostat_mode_updated_time":"41716801611","fan_mode_updated_time":"39315134751","set_point_mode_updated_time":"39729601550","target_cool_temp_updated_time":"39729601550","target_heat_temp_updated_time":"39315134534","current_temp_updated_time":"41679540149","device_temp_unit":"F","endpoint":"0","paired_status":"1","configuration_parameter":"0

    def __init__(self):
        pass