import logging

from datetime import datetime, timezone

from qolsys_controller.observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysPartition(QolsysObservable):

    SYSTEM_STATUS_ARRAY = ['ARM-STAY','ARM-AWAY','DISARM','ARM-AWAY-EXIT-DELAY','ARM-STAY-EXIT-DELAY']
    ALARM_TYPE_ARRAY = ['Police Emergency','Fire Emergency','Auxiliary Emergency','Silent Auxiliary Emergency','Silent Police Emergency']
    ALARM_STATE_ARRAY =['None','Delay','Alarm']
    EXIT_SOUNDS_ARRAY = ['ON','OFF']
    ENTRY_DELAYS_ARRAY = ['ON','OFF']
    
    def __init__(self, 
                 partition_id: int, 
                 name: str, 
                 system_status: str,
                 system_status_changed_time:str,
                 alarm_state:str,
                 alarm_type:list[str],
                 entry_delays:str,
                 exit_sounds:str) -> None:
        
        super().__init__()

        self._id:int = partition_id
        self._name:str = name
        self._system_status:str = system_status
        self._system_status_changed_time:str = system_status_changed_time
        self._exit_sounds:str = exit_sounds
        self._entry_delays:str = entry_delays
        self._alarm_state:str = alarm_state
        self._alarm_type:list[str] = alarm_type
        self._arming_exit_sounds = True

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_status(self) -> str:
        return self._system_status
    
    @property
    def system_status_changed_time(self) -> str:
        return self._system_status_changed_time

    @property
    def alarm_state(self) -> str:
        return self._alarm_state

    @property
    def alarm_type(self) -> list[str]:
        return self._alarm_type
    
    @property
    def exit_sounds(self) -> str:
        return self._exit_sounds
    
    @property
    def arming_exit_sounds(self) -> bool:
        return self._arming_exit_sounds
    
    @property
    def entry_delays(self) -> str:
        return self._entry_delays
    
    @property
    def last_error_type(self):
        return self._last_error_type

    @property
    def last_error_desc(self):
        return self._last_error_desc

    @property
    def last_error_at(self):
        return self._last_error_at

    @property
    def disarm_failed(self):
        return self._disarm_failed

    @system_status.setter
    def system_status(self, value):
        if not value in self.SYSTEM_STATUS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow system_status {value}")
            return

        # if self._system_status != value: # Note
        LOGGER.debug(f"Partition{self._id} ({self._name}) - system_status: {value}")
        self._system_status = value
        self.notify()

    @system_status_changed_time.setter
    def system_status_changed_time(self,value):
        if self._system_status_changed_time != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - system_status_changed_time: {value}")
            self._system_status_changed_time = value
            self.notify()

    @alarm_state.setter
    def alarm_state(self,value):
        if not value in self.ALARM_STATE_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow alarm_state {value}")
            return

        if self._alarm_state != value:
            prev_value = self._alarm_state
            LOGGER.debug(f"Partition{self._id} ({self._name}) - alarm_state: {value}")
            self._alarm_state = value

            # Only notify when None -> Delay and None -> Alarm
            if prev_value != 'Delay':
                self.notify()
   
    @alarm_type.setter
    def alarm_type(self,value:list[str]):
        self._alarm_type = value
        self.notify()
    
    def append_alarm_type(self,value:str):

        if value == '':
            # Default value, panel doesnt send alarm type when user fails to enter disarm code
            value = 'Police Emergency' 

        if not value in self.ALARM_TYPE_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow alarm_type {value}")
            return
        
        self._alarm_type.append(value)
        self.notify()

        for alarm in self._alarm_type:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - alarm_type: {alarm}")

    @exit_sounds.setter
    def exit_sounds(self,value):
        if not value in self.EXIT_SOUNDS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow exit_sounds {value}")
            return

        if self._exit_sounds != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - exit_sound: {value}")
            self._exit_sounds = value
            self.notify()
    
    @arming_exit_sounds.setter
    def arming_exit_sounds(self,value):
        self._arming_exit_sounds = value
    
    @entry_delays.setter
    def entry_delays(self,value):
        if not value in self.ENTRY_DELAYS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow entry_delays {value}")
            return

        if self._entry_delays != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - entry_delays: {value}")
            self._entry_delays = value
            self.notify()

    def is_triggered(self) -> bool:
        return self.alarm_state == 'Alarm'
    
    def is_disarmed(self) -> bool:
        return self.system_status == 'DISARM' and self.alarm_state != 'Alarm'
    
    def is_arming(self) -> bool:
        return self.system_status ==  'ARM-AWAY-EXIT-DELAY' or self.system_status ==  'ARM-STAY-EXIT-DELAY'
    
    def is_pending(self) -> bool:
        return self.alarm_state == 'Delay'
    
    def is_armed_stay(self) -> bool:
        return self.system_status == 'ARM-STAY'
    
    def is_armed_away(self) -> bool:
        return self.system_status == 'ARM-AWAY'

    def __str__(self):
        return (f"<QolsysPartition id={self.id} name={self.name} "
                f"system_status={self.system_status}")