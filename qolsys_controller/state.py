import logging

from .observable import QolsysObservable
from .partition import QolsysPartition
from .zone import QolsysZone
from .zwave_device import QolsysZWaveDevice
from .zwave_dimmer import QolsysDimmer
from .zwave_generic import QolsysGeneric
from .zwave_lock import QolsysLock
from .zwave_thermostat import QolsysThermostat

LOGGER = logging.getLogger(__name__)

class QolsysState(QolsysObservable):

    def __init__(self) -> None:
        super().__init__()

        self._partitions = []
        self._zones = []
        self._zwave_devices = []

        self._state_partition_observer = QolsysObservable()
        self._state_zone_observer = QolsysObservable()
        self._state_zwave_observer = QolsysObservable()

    @property
    def partitions(self) -> list[QolsysPartition]:
        return self._partitions

    @property
    def zwave_devices(self) -> list[QolsysZWaveDevice]:
        return self._zwave_devices

    @property
    def zones(self) -> list[QolsysZone]:
        return self._zones

    @property
    def zwave_dimmers(self) -> list[QolsysDimmer]:
        dimmers = []
        for device in self.zwave_devices:
            if isinstance(device,QolsysDimmer):
                dimmers.append(device)

        return dimmers

    @property
    def zwave_locks(self) -> list[QolsysLock]:
        locks = []
        for device in self.zwave_devices:
            if isinstance(device,QolsysLock):
                locks.append(device)

        return locks

    @property
    def zwave_thermostats(self) -> list[QolsysThermostat]:
        thermostats = []
        for device in self.zwave_devices:
            if isinstance(device,QolsysThermostat):
                thermostats.append(device)

        return thermostats

    @property
    def state_partition_observer(self) -> QolsysObservable:
        return self._state_partition_observer

    @property
    def state_zone_observer(self) -> QolsysObservable:
        return self._state_zone_observer

    @property
    def state_zwave_observer(self) -> QolsysObservable:
        return self._state_zwave_observer

    def partition(self, partition_id:str) -> QolsysPartition:
        for partition in self.partitions:
            if partition.id == partition_id:
                return partition

        return None

    def partition_add(self,new_partition:QolsysPartition) -> None:
        for partition in self.partitions:
            if new_partition.id == partition.id:
                LOGGER.debug("Adding Partition to State, Partition%s (%s) - Allready in Partitions List",new_partition.id,partition.name)
                return

        self.partitions.append(new_partition)
        self.state_partition_observer.notify()

    def partition_delete(self,partition_id:str) -> None:
        partition = self.partition(partition_id)

        if partition is None:
            LOGGER.debug("Deleting Partition from State, Partition%s not found",partition_id)
            return

        self.partitions.remove(partition)
        self.state_partition_observer.notify()

    def zone(self,zone_id:str) -> QolsysZone:
        for zone in self.zones:
            if zone.zone_id == zone_id:
                return zone

        return None

    def zone_add(self, new_zone:QolsysZone) -> None:
        for zone in self.zones:
            if new_zone.zone_id == zone.zone_id:
                LOGGER.debug("Adding Zone to State, zone%s (%s) - Allready in Zone List",new_zone.zone_id,self.sensorname)
                return

        self.zones.append(new_zone)
        self.state_zone_observer.notify()

    def zone_delete(self,zone_id:str) -> None:
        zone = self.zone(zone_id)

        if zone is None:
            LOGGER.debug("Deleting Zone from State, Zone%s not found",zone_id)
            return

        self.zones.remove(zone)
        self.state_zone_observer.notify()

    def zwave_device(self,node_id:str) -> QolsysZWaveDevice:
        for zwave_device in self.zwave_devices:
            if zwave_device.node_id == node_id:
                return zwave_device

        return None

    def zwave_add(self, new_zwave:QolsysZWaveDevice) -> None:
        for zwave_device in self.zwave_devices:
            if new_zwave.node_id == zwave_device.node_id:
                LOGGER.debug("Adding ZWave to State, ZWave%s (%s) - Allready in ZWave List",new_zwave.node_id,zwave_device.node_name)
                return

        self.zwave_devices.append(new_zwave)
        self.state_zwave_observer.notify()

    def zwave_delete(self,node_id:str) -> None:
        zwave = self.zwave_device(node_id)

        if zwave is None:
            LOGGER.debug("Deleting ZWave from State, ZWave%s not found",node_id)
            return

        self.zwave_devices.remove(zwave)
        self.state_zwave_observer.notify()

    def sync_zwave_devices_data(self,db_zwaves:list[QolsysZWaveDevice]) -> None:  # noqa: C901, PLR0912

        db_zwave_list = []
        for db_zwave in db_zwaves:
            db_zwave_list.append(db_zwave.node_id)

        state_zwave_list = []
        for state_zwave in self.zwave_devices:
            state_zwave_list.append(state_zwave.node_id)

        # Update existing ZWave devices
        for state_zwave in self.zwave_devices:
            if state_zwave.node_id in db_zwave_list:
                for db_zwave in db_zwaves:
                    if state_zwave.node_id == db_zwave.node_id:
                        LOGGER.debug("sync_data - update ZWave%s",state_zwave.node_id)

                        # Update Dimmer
                        if isinstance(state_zwave, QolsysDimmer) and isinstance(db_zwave,QolsysDimmer):
                            state_zwave.update_base(db_zwave.to_dict_base())
                            state_zwave.update_dimmer(db_zwave.to_dict_dimmer())
                            break

                        # Update Thermostat
                        if isinstance(state_zwave,QolsysThermostat) and isinstance(db_zwave,QolsysThermostat):
                            state_zwave.update_base(db_zwave.to_dict_base())
                            state_zwave.update_thermostat(db_zwave.to_dict_base())
                            break

                        # Update Lock
                        if isinstance(state_zwave,QolsysLock) and isinstance(db_zwave,QolsysLock):
                            state_zwave.update_base(db_zwave.to_dict_base())
                            state_zwave.update_lock(db_zwave.to_dict_base())
                            break

                        # Generic Z-Wave Device
                        if isinstance(state_zwave,QolsysGeneric) and isinstance(db_zwave,QolsysGeneric):
                            state_zwave.update_base(db_zwave.to_dict_base())
                            break

                        # zwave node_id has changed of node_type, delete and add again
                        # self.zwave_delete(int(state_zwave.node_id))  # noqa: ERA001
                        # self.zwave_add(db_zwave)  # noqa: ERA001

        # Add new zwave device
        for db_zwave in db_zwaves:
            if db_zwave.node_id not in state_zwave_list:
                LOGGER.debug("sync_data - add ZWave%s",db_zwave.node_id)
                self.zwave_add(db_zwave)

        # Delete zwave device
        for state_zwave in self.zwave_devices:
            if state_zwave.node_id not in db_zwave_list:
                LOGGER.debug("sync_data - delete ZWave%s",state_zwave.none_id)
                self.zwave_delete(int(state_zwave.node_id))

    def sync_zones_data(self, db_zones:list[QolsysZone]) -> None:  # noqa: C901
        db_zone_list = []
        for db_zone in db_zones:
            db_zone_list.append(db_zone.zone_id)

        state_zone_list = []
        for state_zone in self.zones:
            state_zone_list.append(state_zone.zone_id)

        # Update existing zones
        for state_zone in self.zones:
            if state_zone.zone_id in db_zone_list:
                for db_zone in db_zones:
                    if state_zone.zone_id == db_zone.zone_id:
                        LOGGER.debug("sync_data - update Zone%s",state_zone.zone_id)
                        state_zone.update(db_zone.to_dict())

        # Delete zones
        for state_zone in self.zones:
            if state_zone.zone_id not in db_zone_list:
                LOGGER.debug("sync_data - delete Zone%s",state_zone.zone_id)
                self.zone_delete(int(state_zone.zone_id))

        # Add new zone
        for db_zone in db_zones:
            if db_zone.zone_id not in state_zone_list:
                LOGGER.debug("sync_data - add Zone%s",db_zone.zone_id)
                self.zone_add(db_zone)

    def sync_partitions_data(self,db_partitions:list[QolsysPartition]) -> None:  # noqa: C901
        db_partition_list = []
        for db_partition in db_partitions:
            db_partition_list.append(db_partition.id)

        state_partition_list = []
        for state_partition in self.partitions:
            state_partition_list.append(state_partition.id)

         # Update existing partitions
        for state_partition in self.partitions:
            if state_partition.id in db_partition_list:
                for db_partition in db_partitions:
                    if state_partition.id == db_partition.id:
                        LOGGER.debug("sync_data - update Partition%s",state_partition.id)
                        state_partition.update_partition(db_partition.to_dict_partition())
                        state_partition.update_settings(db_partition.to_dict_settings())
                        state_partition.alarm_type_array = db_partition.alarm_type_array
                        state_partition.alarm_state = db_partition.alarm_state

        # Delete partitions
        for state_partition in self.partitions:
            if state_partition.id not in db_partition_list:
                LOGGER.debug("sync_data - delete Partition%s",state_partition.id)
                self.partition_delete(state_partition.id)

        # Add new partition
        for db_partition in db_partitions:
            if db_partition.id not in state_partition_list:
                LOGGER.debug("sync_data - Add Partition%s",db_partition.id)
                self.partition_add(db_partition)

    def dump(self) -> None:  # noqa: PLR0915
        LOGGER.debug("*** Information ***")

        for partition in self.partitions:
            pid = partition.id
            name = partition.name
            LOGGER.debug("Partition%s (%s) - system_status: %s",pid,name,partition.system_status)
            LOGGER.debug("Partition%s (%s) - system_status_changed_time: %s",pid,name,partition.system_status_changed_time)
            LOGGER.debug("Partition%s (%s) - alarm_state: %s",pid,name,partition.alarm_state)

            if partition.alarm_type_array == []:
                LOGGER.debug("Partition%s (%s) - alarm_type: %s",pid,name,"None")
            else:
                for alarm_type in partition.alarm_type_array:
                    LOGGER.debug("Partition%s (%s) - alarm_type: %s",pid,name,alarm_type)

            LOGGER.debug("Partition%s (%s) - exit_sounds: %s",pid,name,partition.exit_sounds)
            LOGGER.debug("Partition%s (%s) - entry_delays: %s",pid,name,partition.entry_delays)

        for zone in self.zones:
            zid = zone.zone_id
            name = zone.sensorname
            LOGGER.debug("Zone%s (%s) - status: %s",zid,name,zone.sensorstatus)
            LOGGER.debug("Zone%s (%s) - battery_status: %s",zid,name,zone.battery_status)
            LOGGER.debug("Zone%s (%s) - latestdBm: %s",zid,name,zone.latestdBm)
            LOGGER.debug("Zone%s (%s) - averagedBm: %s",zid,name,zone.averagedBm)

        for zwave in self.zwave_devices:
            if isinstance(zwave,QolsysDimmer):
                nid = zwave.node_id
                name = zwave.dimmer_name
                LOGGER.debug("Dimmer%s (%s) - status: %s",nid,name,zwave.dimmer_status)
                LOGGER.debug("Dimmer%s (%s) - level: %s",nid,name,zwave.dimmer_level)
                LOGGER.debug("Dimmer%s (%s) - paired_status: %s",nid,name,zwave.paired_status)
                LOGGER.debug("Dimmer%s (%s) - node_status: %s",nid,name,zwave.node_status)
                LOGGER.debug("Dimmer%s (%s) - battery_level: %s",nid,name,zwave.node_battery_level)
                LOGGER.debug("Dimmer%s (%s) - battery_level_value: %s",nid,name,zwave.node_battery_level_value)
                continue

            if isinstance(zwave, QolsysThermostat):
                zid = zwave.thermostat_node_id
                name = zwave.thermostat_name
                LOGGER.debug("Thermostat%s (%s) - current_temp: %s",zid,name,zwave.thermostat_current_temp)
                LOGGER.debug("Thermostat%s (%s) - mode: %s",zid,name,zwave.thermostat_mode)
                LOGGER.debug("Thermostat%s (%s) - fan_mode: %s",zid,name,zwave.thermostat_fan_mode)
                LOGGER.debug("Thermostat%s (%s) - target_temp: %s",zid,name,zwave.thermostat_target_temp)
                LOGGER.debug("Thermostat%s (%s) - target_cool_temp: %s",zid,name,zwave.thermostat_target_cool_temp)
                LOGGER.debug("Thermostat%s (%s) - target_heat_temp: %s",zid,name,zwave.thermostat_target_heat_temp)
                LOGGER.debug("Thermostat%s (%s) - set_point_mode: %s",zid,name,zwave.thermostat_set_point_mode)
                continue

            if isinstance(zwave, QolsysLock):
                zid = zwave.lock_node_id
                name = zwave.lock_name
                LOGGER.debug("Lock%s (%s) - current_temp: %s",zid,name,zwave.lock_status)
                continue

            if isinstance(zwave, QolsysGeneric):
                zid = zwave.node_id
                name = zwave.node_name
                LOGGER.debug("Generic%s (%s) - node_type: %s",zid,name,zwave.node_type)
                LOGGER.debug("Generic%s (%s) - status: %s",zid,name,zwave.node_status)
                LOGGER.debug("Generic%s (%s) - battery_level: %s",zid,name,zwave.node_battery_level)
                LOGGER.debug("Generic%s (%s) - battery_level_vale: %s",zid,name,zwave.node_battery_level_value)
                continue
