import logging

from datetime import datetime, timezone

from qolsys_controller.observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysPartition(QolsysObservable):

    NOTIFY_UPDATE_ATTRIBUTES = 'update_attributes'
    NOTIFY_UPDATE_SYSTEM_STATUS = 'update_system_status'
    NOTIFY_UPDATE_SYSTEM_STATUS_CHANGED_TIME = 'update_system_status_changed_time'
    NOTIFY_UPDATE_ALARM_STATE = 'update_alarm_state'
    NOTIFY_UPDATE_ALARM_TYPE = 'update_alarm_type'
    NOTIFY_UPDATE_EXIT_SOUNDS = 'update_exit_sounds'
    NOTIFY_UPDATE_ENTRY_DELAYS = 'update_entry_delays'

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
        self._alarm_sate:str = alarm_state
        self._alarm_type:list[str] = alarm_type
    
        self._last_error_type = None
        self._last_error_desc = None
        self._last_error_at = None
        self._disarm_failed = 0

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
        return self._alarm_sate

    @property
    def alarm_type(self) -> list[str]:
        return self._alarm_type
    
    @property
    def exit_sounds(self) -> str:
        return self._exit_sounds
    
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
        prev_value = self._system_status
        self._system_status = value
        self.notify(change=self.NOTIFY_UPDATE_SYSTEM_STATUS,partition_id=self.id,new_value=value,prev_value=prev_value)

        # If the panel is disarmed, we can reset the failed disarm attempts
        #if value == 'DISARM':
        #    self.disarm_failed = 0

        #self.alarm_type = None

    @system_status_changed_time.setter
    def system_status_changed_time(self,value):
        if self._system_status_changed_time != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - system_status_changed_time: {value}")
            prev_value = self._system_status
            self._system_status_changed_time = value
            self.notify(change=self.NOTIFY_UPDATE_SYSTEM_STATUS_CHANGED_TIME,partition_id=self.id,new_value=value,prev_value=prev_value)

    @alarm_state.setter
    def alarm_state(self,value):
        if not value in self.ALARM_STATE_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow alarm_state {value}")
            return

        if self._alarm_sate != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - alarm_state: {value}")
            prev_value = self._alarm_sate
            self._alarm_sate = value
            self.notify(change=self.NOTIFY_UPDATE_ALARM_STATE,partition_id=self.id,new_value=value,prev_value=prev_value)

    def append_alarm_type(self,value:str):
        if not value in self.ALARM_TYPE_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow alarm_type {value}")
            return
        
        prev_value = self._alarm_type
        self._alarm_type.append(value)
        self.notify(change=self.NOTIFY_UPDATE_ALARM_TYPE,partition_id=self.id,new_value=self._alarm_type,prev_value=prev_value)

        for alarm in self._alarm_type:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - alarm_type: {alarm}")

    @exit_sounds.setter
    def exit_sounds(self,value):
        if not value in self.EXIT_SOUNDS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow exit_sounds {value}")
            return

        if self._exit_sounds != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - exit_sound: {value}")
            prev_value = self._exit_sounds
            self._exit_sounds = value
            self.notify(change=self.NOTIFY_UPDATE_EXIT_SOUNDS,partition_id=self.id,new_value=value,prev_value=prev_value)
    
    @entry_delays.setter
    def entry_delays(self,value):
        if not value in self.ENTRY_DELAYS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow entry_delays {value}")
            return

        if self._entry_delays != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - entry_delays: {value}")
            prev_value = self._entry_delays
            self._entry_delays = value
            self.notify(change=self.NOTIFY_UPDATE_ENTRY_DELAYS,partition_id=self.id,new_value=value,prev_value=prev_value)

    @disarm_failed.setter
    def disarm_failed(self, value):
        new_value = int(value)

        if self._disarm_failed != new_value:
            LOGGER.debug(f"Partition '{self.id}' ({self.name}) disarm failed updated to '{value}'")
            self._disarm_failed = new_value

            self.notify(change=self.NOTIFY_UPDATE_ATTRIBUTES)

    def errored(self, error_type: str, error_description: str):
        self._last_error_type = error_type
        self._last_error_desc = error_description
        self._last_error_at = datetime.now(timezone.utc).isoformat()

        # If this is a failed disarm attempt, let's increase the counter
        if error_type.upper() == 'DISARM_FAILED':
            self._disarm_failed += 1

        self.notify(change=self.NOTIFY_UPDATE_ATTRIBUTES)

    def __str__(self):
        return (f"<QolsysPartition id={self.id} name={self.name} "
                f"system_status={self.system_status}")