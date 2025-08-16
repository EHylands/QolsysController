import logging

from qolsys_controller.observable import QolsysObservable
from qolsys_controller.partition import QolsysPartition
from qolsys_controller.zone import QolsysZone
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
        self._zwave_devices = []

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
        return self._zwave_devices
    
    @property
    def zwave_dimmers(self) -> list[QolsysDimmer]:
        dimmers = []
        for device in self.zwave_devices:
            if isinstance(device,QolsysDimmer):
                dimmers.append(device)
        
        return dimmers

    def partition(self, partition_id:int):
        return self._partitions.get(partition_id)
    
    def zwave_device(self,node_id:int):
        for zwave_device in self.zwave_devices:
            if int(zwave_device.node_id) == node_id:
                return zwave_device

        return None

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

    def partition_delete(self,partition_id:int):
        partition = self.partitions[partition_id]

        if partition is None:
            LOGGER.debug(f'Deleting Partition from State, Partition{partition.id} not found')
            return

        self._partitions.remove(partition)
        self.state_partition_observer.notify(change = self.NOTIFY_PARTITION_DELETE, partition = partition)

    def zone_add(self, new_zone):
        for zone in self.zones:
            if new_zone.zone_id == zone.zone_id:
                LOGGER.debug(f"Adding Zone to State, zone{new_zone.zone_id} ({self._sensorname}) - Allready in Zone List")
                return
            
        self._zones[int(new_zone.zone_id)] = new_zone
        self.state_zone_observer.notify(change=self.NOTIFY_ZONE_ADD,zone=new_zone)

    def zone_delete(self,zone_id:int):
        zone = self.zones[zone_id]

        if zone is None:
            LOGGER.debug(f'Deleting Zone from State, Zone{zone_id} not found')
            return

        self._zones.remove(zone)
        self.state_zone_observer.notify(change=self.NOTIFY_PARTITION_DELETE,zone=zone)

    def zwave_add(self, new_zwave):
        for zwave_device in self.zwave_devices:
            if new_zwave.node_id == zwave_device.node_id:
                LOGGER.debug(f"Adding ZWave to State, ZWave{new_zwave.node_id} ({zwave_device._node_name}) - Allready in ZWave List")
                return
            
        self._zwave_devices.append(new_zwave)
        #self.state_zone_observer.notify()

    def zwave_delete(self,node_id:int):        
        zwave = self.zwave_device(node_id)

        if zwave is None:
            LOGGER.debug(f'Deleting ZWave from State, ZWave{node_id} not found')
            return

        self._zwave_devices.remove(zwave)
        #self.state_zone_observer.notify(change=self.NOTIFY_PARTITION_DELETE,zone=zone)

    def load_data(self,db_partitions:list[QolsysPartition],db_zones:list[QolsysZone],db_zwaves:list[QolsysZWaveDevice]):

        db_partition_list = []
        for db_partition in db_partitions:
            db_partition_list.append(db_partition.id)

        state_partition_list = []
        for state_partition in self.partitions:
            state_partition_list.append(state_partition.id)

        db_zone_list = []
        for db_zone in db_zones:
            db_zone_list.append(db_zone.zone_id)

        state_zone_list = []
        for state_zone in self.zones:
            state_zone_list.append(state_zone.zone_id)

        db_zwave_list = []
        for db_zwave in db_zwaves:
            db_zwave_list.append(db_zwave.node_id)

        state_zwave_list = []
        for state_zwave in self.zwave_devices:
            state_zwave_list.append(state_zwave.node_id)


        # Update existing partitions
        for state_partition in self.partitions:
            if state_partition.id in db_partition_list:
                for db_partition in db_partitions:
                    if state_partition.id == db_partition.id:
                        LOGGER.debug(f'load_data - update Partition{state_partition.id}')
                        state_partition.update(db_partition.to_dict())
              
        # Delete partitions
        for state_partition in self.partitions:
            if state_partition.id not in db_partition_list:
                LOGGER.debug(f'load_data - delete Partition{state_partition.id}')
                self.partition_delete(int(state_partition.id))
            
        # Add new partition
        for db_partition in db_partitions:
            if db_partition.id not in state_partition_list:
                LOGGER.debug(f'load_data - add Partition{db_partition.id}')
                self.partition_add(db_partition)

        # Update existing zones
        for state_zone in self.zones:
            if state_zone.zone_id in db_zone_list:
                for db_zone in db_zones:
                    if state_zone.zone_id == db_zone.zone_id:
                        LOGGER.debug(f'load_data - update Zone{state_zone.zone_id}')
                        state_zone.update(db_zone.to_dict())

        # Delete zones
        for state_zone in self.zones:
            if state_zone.zone_id not in db_zone_list:
                LOGGER.debug(f'load_data - delete Zone{state_zone.zone_id}')
                self.zone_delete(int(state_zone.zone_id))
            
        # Add new zone
        for db_zone in db_zones:
            if db_zone.zone_id not in state_zone_list:
                LOGGER.debug(f'load_data - add Zone{db_zone.zone_id}')
                self.zone_add(db_zone)

        # Update existing ZWave devices
        for state_zwave in self.zwave_devices:
            if state_zwave.node_id in db_zwave_list:
                for db_zwave in db_zwaves:
                    if state_zwave.node_id == db_zwave.node_id:
                        LOGGER.debug(f'load_data - update ZWave{state_zwave.node_id}')

                        if isinstance(state_zwave, QolsysDimmer) and isinstance(db_zwave,QolsysDimmer):
                            state_zwave.update_base(db_zwave.to_dict_base())
                            state_zwave.update_dimmer(db_zwave.to_dict_dimmer())
                            break

                        # zwave node_id has changed of node_type, delete and add again
                        #self.zwave_delete(int(state_zwave.node_id))
                        #self.zwave_add(db_zwave)

        # Add new zwave device
        for db_zwave in db_zwaves:
            if db_zwave.node_id not in state_zwave_list:
                LOGGER.debug(f'load_data - add ZWave{db_zwave.node_id}')
                self.zwave_add(db_zwave)

        # Delete zwave device
        for state_zwave in self.zwave_devices:
            if state_zwave.node_id not in db_zwave_list:
                LOGGER.debug(f'load_data - delete ZWave{state_zwave.none_id}')
                self.zwave_delete(int(state_zwave.node_id))
        
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
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - status: {zwave._dimmer_status} ")
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - level: {zwave._dimmer_level}")
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - paired_status: {zwave._paired_status}")
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - node_status: {zwave._node_status}")
                        LOGGER.debug(f"ZWaveDimmer{zwave._node_id} ({zwave._dimmer_name}) - battery_level: {zwave._node_battery_level}")



