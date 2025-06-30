import logging

from qolsys.event import QolsysEvent
from qolsys.exceptions import UnableToParseEventException

LOGGER = logging.getLogger(__name__)

class QolsysEventSyncDB(QolsysEvent):

    def __init__(self, request_id: str, raw_event: dict) -> None:
        super().__init__(request_id, raw_event)

    def database_frome_json(self,data):
        event_type = data.get('eventName')
        
        if event_type != 'syncdatabase':
            raise UnableToParseEventException(f"Cannot parse event '{event_type}'")

        return data.get('fulldbdata')      

