import logging

from .enum import (
    PartitionAlarmState,
    PartitionAlarmType,
    PartitionSystemStatus,
)
from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysPartition(QolsysObservable):

    EXIT_SOUNDS_ARRAY = ["ON","OFF",""]  # noqa: RUF012
    ENTRY_DELAYS_ARRAY = ["ON","OFF",""]  # noqa: RUF012

    def __init__(self,partition_dict:dict,settings_dict:dict,alarm_state:PartitionAlarmState,alarm_type_array:list[PartitionAlarmType]) -> None:

        super().__init__()

        # Partition info (partition table)
        self._id:str = partition_dict.get("partition_id")
        self._name:str = partition_dict.get("name")
        self._devices = partition_dict.get("devices")

        # Partition Settings (qolsyssettings table)
        self._system_status:PartitionSystemStatus = PartitionSystemStatus(settings_dict.get("SYSTEM_STATUS",""))
        self._system_status_changed_time:str = settings_dict.get("SYSTEM_STATUS_CHANGED_TIME","")
        self._exit_sounds:str = settings_dict.get("EXIT_SOUNDS","")
        self._entry_delays:str = settings_dict.get("ENTRY_DELAYS","")

        # Alarm State (state table)
        self._alarm_state:PartitionAlarmState = alarm_state

        # Alarm Type (alarmedsensor table)
        self._alarm_type_array:list[PartitionAlarmType] = alarm_type_array

        # Other
        self._command_exit_sounds = True
        self._command_arm_stay_instant = True

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_status(self) -> PartitionSystemStatus:
        return self._system_status

    @property
    def system_status_changed_time(self) -> str:
        return self._system_status_changed_time

    @property
    def alarm_state(self) -> PartitionAlarmState:
        return self._alarm_state

    @property
    def alarm_type_array(self) -> list[PartitionAlarmType]:
        return self._alarm_type_array

    @property
    def exit_sounds(self) -> str:
        return self._exit_sounds

    @property
    def entry_delays(self) -> str:
        return self._entry_delays

    @property
    def command_exit_sounds(self) -> bool:
        return self._command_exit_sounds

    @property
    def command_arm_stay_instant(self) -> bool:
        return self._command_arm_stay_instant

    @system_status.setter
    def system_status(self, new_value:PartitionSystemStatus) -> None:
        if self._system_status != new_value:
            LOGGER.debug("Partition%s (%s) - system_status: %s",self.id,self.name,new_value)
            self._system_status = new_value
            self.notify()

    @system_status_changed_time.setter
    def system_status_changed_time(self,value:str) -> None:
        if self._system_status_changed_time != value:
            LOGGER.debug("Partition%s (%s) - system_status_changed_time: %s",self._id,self._name,value)
            self._system_status_changed_time = value
            self.notify()

    @alarm_state.setter
    def alarm_state(self,new_value:PartitionAlarmState) -> None:
        if self._alarm_state != new_value:
            LOGGER.debug("Partition%s (%s) - alarm_state: %s",self.id,self.name,new_value)
            self._alarm_state = new_value
            self.notify()

    @alarm_type_array.setter
    def alarm_type_array(self,new_alarm_type_array:list[PartitionAlarmType]) -> None:

        # If no changes are detected: return without notification
        if sorted(new_alarm_type_array, key=lambda c: c.value) == sorted(self.alarm_type_array,key=lambda c: c.value):
            return

        # alarm_type_array are different:
        self._alarm_type_array = []

        # If all alarm have been cleared
        if new_alarm_type_array == []:
            LOGGER.debug("Partition%s (%s) - alarm_type: %s",self._id,self._name,"None")
            self.notify()
            return

        self.append_alarm_type(new_alarm_type_array)

    @name.setter
    def name(self,value:str) -> None:
         if self._name != value:
            LOGGER.debug("Partition%s (%s) - name: %s",self._id,self._name,value)
            self._name = value
            self.notify()

    def append_alarm_type(self,new_alarm_type_array:list[PartitionAlarmType]) -> None:

        data_changed = False

        for new_alarm_type in new_alarm_type_array:

            # Value already in array
            if new_alarm_type in self._alarm_type_array:
                continue

            self._alarm_type_array.append(new_alarm_type)
            data_changed = True

        if data_changed:
            self.notify()
            for alarm in self._alarm_type_array:
                LOGGER.debug("Partition%s (%s) - alarm_type: %s",self._id,self._name,alarm)

    @exit_sounds.setter
    def exit_sounds(self,value:str) -> None:
        if value not in self.EXIT_SOUNDS_ARRAY:
            LOGGER.debug("Partition%s (%s) - Unknow exit_sounds %s",self._id,self._name,value)
            return

        if self._exit_sounds != value:
            LOGGER.debug("Partition%s (%s) - exit_sound: %s",self._id,self._name,value)
            self._exit_sounds = value
            self.notify()

    @entry_delays.setter
    def entry_delays(self,value:str) -> None:
        if value not in self.ENTRY_DELAYS_ARRAY:
            LOGGER.debug("Partition%s (%s) - Unknow entry_delays %s",self._id,self._name,value)
            return

        if self._entry_delays != value:
            LOGGER.debug("Partition%s (%s) - entry_delays: %s",self._id,self._name,value)
            self._entry_delays = value
            self.notify()

    @command_exit_sounds.setter
    def command_exit_sounds(self,value:str) -> None:
        self._command_exit_sounds = value
        LOGGER.debug("Partition%s (%s) - command_exit_sounds: %s",self._id,self._name,value)
        self.notify()

    @command_arm_stay_instant.setter
    def command_arm_stay_instant(self,value:str) -> None:
        self._command_arm_stay_instant = value
        LOGGER.debug("Partition%s (%s) - arm_stay_instant: %s",self._id,self._name,value)
        self.notify()

    def update_partition(self,data:dict) -> None:
        # Check if we are updating same partition_id
        partition_id_update = data.get("partition_id","")
        if int(partition_id_update) != int(self.id):
            LOGGER.error("Updating Partition%s (%s) with Partition '%s' (different id)",self._id,self._name,partition_id_update)
            return

        self.start_batch_update()

        # Update Partition Name
        if "name" in data:
            self.name = data.get("name")

        # Update Partition Devices
        if "devices" in data:
            self._devices = data.get("devices")

        self.end_batch_update()

    def update_settings(self,data:dict) -> None:

        self.start_batch_update()

        # Update system_status
        if "SYSTEM_STATUS" in data:
            self.system_status = data.get("SYSTEM_STATUS")

        # Update system_status_changed_time
        if "SYSTEM_STATUS_CHANGED_TIME" in data:
            self.system_status_changed_time = data.get("SYSTEM_STATUS_CHANGED_TIME")

        # Update exit_sounds
        if "EXIT_SOUNDS" in data:
            self.exit_sounds = data.get("EXIT_SOUNDS")

        # Update entry_delays
        if "ENTRY_DELAYS" in data:
            self.entry_delays = data.get("ENTRY_DELAYS")

        self.end_batch_update()

    def to_dict_partition(self) -> dict:
        return {
            "partition_id": self.id,
            "name": self.name,
            "devices": self._devices,
        }

    def to_dict_settings(self) -> dict:
        return {
            "SYSTEM_STATUS":self.system_status.value,
            "SYSTEM_STATUS_CHANGED_TIME" : self.system_status_changed_time,
            "EXIT_SOUNDS":self.exit_sounds,
            "ENTRY_DELAYS":self.entry_delays,
        }
