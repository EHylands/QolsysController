import logging

from qolsys_controller.observable import QolsysObservable
from qolsys_controller.partition import QolsysPartition
from qolsys_controller.zone import QolsysSensor
from qolsys_controller.zwave_dimmer import QolsysDimmer
from qolsys_controller.zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysState(QolsysObservable):
    NOTIFY_PARTITION_ADD = 'partition_add'
    NOTIFY_PARTITION_DELETE = 'partition_delete'
    NOTIFY_ZONE_ADD = 'zone_add'
    NOTIFY_ZONE_DELETE = 'zone_delete'
    
    NOTIFY_UPDATE_ERROR = 'update_error'
    NOTIFY_UPDATE_PARTITIONS = 'update_partitions'

    def __init__(self):
        super().__init__()

        self._last_exception = None

        self._partitions = {}
        self._zones = {}
        self._zwave_devices = {}

        self.state_partition_observer = QolsysObservable()
        self.state_zone_observer = QolsysObservable()

    @property
    def last_exception(self):
        return self._last_exception

    @last_exception.setter
    def last_exception(self, value):
        prev_value = self._last_exception
        self._last_exception = value

        self.notify(change=self.NOTIFY_UPDATE_ERROR,
                    prev_value=prev_value,
                    new_value=value)

    @property
    def partitions(self):
        return self._partitions.values()
    
    @property
    def zwave_devices(self):
        return self._zwave_devices.values()

    def partition(self, partition_id:int):
        return self._partitions.get(partition_id)
    
    def zwave_device(self,node_id:int):
        return self._zwave_devices.get(node_id)
    
    @property
    def zones(self):
        return self._zones.values()
        
    def zone(self,zone_id:int):
        return self._zones.get(zone_id)

    def partition_add(self,new_partition:QolsysPartition):
        for partition in self.partitions:
            if partition.id == new_partition.id:
                LOGGER.debug(f"Adding Partition to State, Partition{new_partition.id} ({partition.name}) - Allready in Partitions List")
                return

        self._partitions[int(new_partition.id)] = new_partition
        self.state_partition_observer.notify(change = self.NOTIFY_PARTITION_ADD, partition = new_partition)

    def partition_delete(self,partition:QolsysPartition):
        partition = self.partitions[int(partition.id)]

        if partition is None:
            LOGGER.debug(f'Deleting Partition from State, Partition{partition.id} not found')
            return

        self._partitions.remove(partition)
        self.state_partition_observer.notify(change = self.NOTIFY_PARTITION_DELETE, partition = partition)

    def zone_add(self, new_zone):
        for zone in self.zones():
            if new_zone.zone_id == zone.zone_id:
                LOGGER.debug(f"Adding Zone to State, zone{new_zone.zone_id} ({self._sensorname}) - Allready in Zone List")
                return
            
        self._zone.append(new_zone)
        self.state_zone_observer.notify(change=self.NOTIFY_ZONE_ADD,zone=zone)

    def zone_delete(self,zone_id:str):
        zone = self.zones[int(zone_id)]

        if zone is None:
            LOGGER.debug(f'Deleting Zone from State, Zone{zone_id} not found')
            return

        self._zones[zone.zone_id].remove(zone)
        self.state_zone_observer.notify(change=self.NOTIFY_PARTITION_DELETE,zone=zone)

    def load_data(self,partitions:list[QolsysPartition],zones:list[QolsysSensor],zwaves:list[QolsysZWaveDevice]):
                
        self._partitions = {}
        for partition in partitions:
            self.partition_add(partition)
        
        self._zones = {}
        for zone in zones:
            self._zones[int(zone.zone_id)] = zone
            # zone add notification
            self.state_zone_observer.notify(change=self.NOTIFY_ZONE_ADD,zone=zone)

        self._zwave_devices = {}
        for zwave in zwaves:
            self._zwave_devices[int(zwave.base_node_id)] = zwave
           
    def dump(self):
        LOGGER.debug(f'*** Information ***')

        for partition in self.partitions:  
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - system_status: {partition.system_status}")
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - system_status_changed_time: {partition.system_status_changed_time}")
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - alarm_state: {partition.alarm_state}")
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - exit_sounds: {partition.exit_sounds}")
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - entry_delays: {partition.entry_delays}")

            for type in partition.alarm_type:
                LOGGER.debug(f"Partition{partition._id} ({partition._name}) - alarm_type: {type}")

        for zone in self.zones:
            LOGGER.debug(f"Zone{zone.zone_id} ({zone._sensorname}) - {zone._sensorstatus}")

        for zwave in self.zwave_devices:
            if isinstance(zwave,QolsysDimmer):
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - status:{zwave._dimmer_status} ")
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - level:{zwave._dimmer_level}")


