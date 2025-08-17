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
        self._command_exit_sounds = True
        self._command_arm_stay_instant = True

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
    def entry_delays(self) -> str:
        return self._entry_delays
    
    @property
    def command_exit_sounds(self) -> bool:
        return self._command_exit_sounds
    
    @property   
    def command_arm_stay_instant(self) -> bool:
        return self._command_arm_stay_instant
    
    def to_dict(self) -> dict:
        return {
            'partition_id': self.id,
            'name':self.name,
            'system_status':self.system_status,
            'system_status_changed_time' : self.system_status_changed_time,
            'exit_sounds':self.exit_sounds,
            'entry_delays':self.entry_delays,
            'alarm_type':self.alarm_type,
            'alarm_state':self.alarm_state
        }
    
    def update(self,values:dict):
        # Check if we are updating same partition_id
        partition_id_update = values.get('partition_id','')
        if int(partition_id_update) != int(self._id):
            LOGGER.error(f"Updating Partition '{self._id}' ({self._name}) with Partition '{partition_id_update}' (different id)")
            return
        
        self.start_batch_update()
        
        # Update Partition Name
        if 'name' in values:
            self.name = values.get('name')

        # Update system_status
        if 'system_status' in values:
            self.system_status = values.get('system_status')

        # Update system_status_changed_time
        if 'system_status_changed_time' in values:
            self.system_status_changed_time = values.get('system_status_changed_time')

        # Update exit_sounds
        if 'exit_sounds' in values:
            self.exit_sounds = values.get('exit_sounds')

        # Update entry_delays
        if 'entry_delays' in values:
            self.entry_delays = values.get('entry_delays')

        # Update alarm_type
        if 'alarm_type' in values:
            self.alarm_type = values.get('alarm_type')

        # Update alarm_state 
        if 'alarm_state' in values:
            self.alarm_state  = values.get('alarm_state')

        self.end_batch_update()
    
    @system_status.setter
    def system_status(self, value):
        if not value in self.SYSTEM_STATUS_ARRAY:
            LOGGER.error(f"Partition{self._id} ({self._name}) - Unknow system_status {value}")
            return

        if self._system_status != value: # Note
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
            if self.system_status == 'ARM-AWAY-EXIT-DELAY' or self.system_status == 'ARM-STAY-EXIT-DELAY':
                if prev_value == 'Delay' and value == 'None':
                    return
            
            self.notify()
   
    @alarm_type.setter
    def alarm_type(self,value:list[str]):
        self._alarm_type = value
        self.notify()

    @name.setter
    def name(self,value):
         if self._name != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - name: {value}")
            self._name = value
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
    
    @entry_delays.setter
    def entry_delays(self,value):
        if not value in self.ENTRY_DELAYS_ARRAY:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - Unknow entry_delays {value}")
            return

        if self._entry_delays != value:
            LOGGER.debug(f"Partition{self._id} ({self._name}) - entry_delays: {value}")
            self._entry_delays = value
            self.notify()

    @command_exit_sounds.setter
    def command_exit_sounds(self,value):
        if self._command_exit_sounds != value:
            self._command_exit_sounds = value
            self.notify()

    @command_arm_stay_instant.setter
    def command_arm_stay_instant(self,value):
        if self._command_arm_stay_instant != value:
            self._command_arm_stay_instant = value
            self.notify()

    def is_triggered(self) -> bool:
        return self.alarm_state == 'Alarm'
    
    def is_disarmed(self) -> bool:
        return self.system_status == 'DISARM' and self.alarm_state != 'Alarm'
    
    def is_arming(self) -> bool:
        return self.system_status ==  'ARM-AWAY-EXIT-DELAY' or self.system_status ==  'ARM-STAY-EXIT-DELAY'
    
    def is_pending(self) -> bool:
        return False
        
    def is_armed_stay(self) -> bool:
        return self.system_status == 'ARM-STAY'
    
    def is_armed_away(self) -> bool:
        return self.system_status == 'ARM-AWAY'

    def __str__(self):
        return (f"<QolsysPartition id={self.id} name={self.name} "
                f"system_status={self.system_status}")