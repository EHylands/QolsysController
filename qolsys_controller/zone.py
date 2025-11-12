import asyncio
import logging

from .enum import DeviceCapability, ZoneSensorGroup, ZoneSensorType, ZoneStatus
from .observable import QolsysObservable
from .settings import QolsysSettings

LOGGER = logging.getLogger(__name__)


class QolsysZone(QolsysObservable):

    def __init__(self, data: dict, settings: QolsysSettings) -> None:  # noqa: PLR0915
        super().__init__()

        self._settings = settings
        self._delay_task:asyncio.Task = None

        self._zone_id: str = data.get("zoneid", "")
        self._sensorname: str = data.get("sensorname", "")
        self._sensorstatus: ZoneStatus = ZoneStatus(data.get("sensorstatus", ""))
        self._sensortype = ZoneSensorType(data.get("sensortype", ""))
        self._sensorgroup: str = data.get("sensorgroup", "")
        self._battery_status: str = data.get("battery_status", "")
        self._averagedBm: str = data.get("averagedBm", "")
        self._latestdBm: str = data.get("latestdBm", "")
        self._ac_status: str = data.get("ac_status", "")
        self._shortID: str = data.get("shortID", "")
        self._device_capability: str = data.get("device_capability", "")
        self._current_capability: str = data.get("current_capability", "")

        self._id = data.get("_id", "")
        self._zone_type = data.get("zone_type", "")
        self._sensor_id = data.get("sensorid", "")
        self._sensorstate = data.get("sensorstate", "")
        self._zone_physical_type = data.get("zone_physical_type", "")
        self._zone_alarm_type = data.get("zone_alarm_type", "")
        self._partition_id = data.get("partition_id", "")
        self._sensortts = data.get("sensortts", "")
        self._zone_rf_sensor = data.get("zone_rf_sensor", "")
        self._zone_supervised = data.get("zone_supervised", "")
        self._zone_reporting_enabled = data.get("zone_reporting_enabled", "")
        self._zone_two_way_voice_enabled = data.get("zone_two_way_voice_enabled", "")
        self._signal_source = data.get("signal_source", "")
        self._serial_number = data.get("serial_number", "")
        self._chimetype = data.get("chimetype", "")
        self._frame_count = data.get("frame_count", "")
        self._frame_type = data.get("frame_type", "")
        self._frame_id = data.get("frame_id", "")
        self._allowdisarming = data.get("allowdisarming", "")
        self._time = data.get("time", "")
        self._version = data.get("version", "")
        self._opr = data.get("opr", "")
        self._zone_equipement_code = data.get("zone_equipment_code", "")
        self._created_date = data.get("created_date", "")
        self._created_by = data.get("created_by", "")
        self._updated_by = data.get("updated_by", "")
        self._updated_date = data.get("updated_date", "")
        self._diag_24hr = data.get("diag_24hr", "")
        self._sub_type = data.get("sub_type", "")
        self._powerg_manufacture_id = data.get("powerg_manufacture_id", "")
        self._parent_node = data.get("parent_node", "")
        self._extras = data.get("extras", "")

        # EXTRA POWERG ATTRIBUTES
        self._powerg_long_id: str = ""
        self._powerg_status_data: str = ""
        self._powerg_temperature: str = ""
        self._powerg_light: str = ""
        self._powerg_notification_period: str = ""
        self._powerg_average_link_quality: str = ""
        self._powerg_link_quality: str = ""
        self._powerg_link_status: str = ""
        self._powerg_battery_voltage: str = ""

    def is_powerg_enabled(self) -> bool:
        return self._current_capability == DeviceCapability.POWERG

    def is_powerg_temperature_enabled(self) -> bool:
        return self._powerg_temperature != ""

    def is_powerg_light_enabled(self) -> bool:
        return self._powerg_light != ""

    def is_average_dbm_enabled(self) -> bool:
        return self.averagedBm is not None

    def is_latest_dbm_enabled(self) -> bool:
        return self.latestdBm is not None

    def is_battery_enabled(self) -> bool:
        return self.battery_status != ""

    def is_ac_enabled(self) -> bool:
        return self.ac_status != ""

    def update_powerg(self, data: dict) -> None:
        short_id_update = data.get("shortID", "")
        if short_id_update != self.shortID:
            LOGGER.error("Updating Zone%s PowerG Attribute (%s) with Zone%s (different shortID)", self._zone_id, self.sensorname, short_id_update)
            return

        self.start_batch_update()

        if "longID" in data:
            self._powerg_long_id = data.get("longID")

        if "status_data" in data:
            self.powerg_status_data = data.get("status_data")

        if "temperature" in data:
            self.powerg_temperature = data.get("temperature")

        if "light" in data:
            self.powerg_light = data.get("light")

        if "notification_period" in data:
            self._powerg_notification_period = data.get("notification_period")

        if "average_link_quality" in data:
            self._powerg_average_link_quality = data.get("average_link_quality")

        if "link_quality" in data:
            self._powerg_link_quality = data.get("link_quality")

        if "link_status" in data:
            self._powerg_link_status = data.get("link_status")

        if "battery_voltage" in data:
            self._powerg_battery_voltage = data.get("battery_voltage")

        self.end_batch_update()

    def update(self, data: dict) -> None:  # noqa: C901, PLR0912, PLR0915
        zone_id_update = data.get("zoneid", "")
        if zone_id_update != self._zone_id:
            LOGGER.error("Updating Zone%s (%s) with Zone%s (different id)", self._zone_id, self.sensorname, zone_id_update)
            return

        self.start_batch_update()

        if "sensorname" in data:
            self.sensorname = data.get("sensorname")

        if "sensorstatus" in data:
            self.sensorstatus = ZoneStatus(data.get("sensorstatus"))

        if "battery_status" in data:
            self.battery_status = data.get("battery_status")

        if "time" in data:
            self.time = data.get("time")

        if "partition_id" in data:
            self._partition_id = data.get("partition_id")

        if "lastestdBm" in data:
            self.latestdBm = data.get("latestdBm")

        if "averagedBm" in data:
            self.averagedBm = data.get("averagedBm")

        if "sensorgroup" in data:
            self.sensorgroup = data.get("sensorgroup")

        if "sensorstate" in data:
            self._sensorstate = data.get("sensorstate")

        if "sensortype" in data:
            self.sensortype = ZoneSensorType(data.get("sensortype"))

        if "zone_type" in data:
            self._zone_type = data.get("zone_type")

        if "zone_physical_type" in data:
            self._zone_physical_type = data.get("zone_physical_type")

        if "zone_alarm_type" in data:
            self._zone_alarm_type = data.get("zone_alarm_type")

        if "sensorttss" in data:
            self._sensortts = data.get("sensortts")

        if "current_capability" in data:
            self._current_capability = data.get("current_capability")

        if "zone_rf_sensor" in data:
            self._zone_rf_sensor = data.get("zone_rf_sensor")

        if "zone_supervised" in data:
            self._zone_supervised = data.get("zone_supervised")

        if "zone_reporting_enabled" in data:
            self._zone_reporting_enabled = data.get("zone_reporting_enabled")

        if "zone_two_way_voice_enabled" in data:
            self._zone_two_way_voice_enabled = data.get("zone_two_way_voice_enabled")

        if "signal_source" in data:
            self._signal_source = data.get("signal_source")

        if "serial_number" in data:
            self._serial_number = data.get("serial_number")

        if "chimetype" in data:
            self._chimetype = data.get("chimetype")

        if "frame_count" in data:
            self._frame_count = data.get("frame_count")

        if "frame_type" in data:
            self._frame_type = data.get("frame_type")

        if "allowdisarming" in data:
            self._allowdisarming = data.get("allowdisarming")

        self.end_batch_update()

    @property
    def id(self) -> str:
        return self._id

    @property
    def sensorname(self) -> str:
        return self._sensorname

    @property
    def sensorgroup(self) -> str:
        return self._sensorgroup

    @property
    def sensorstatus(self) -> ZoneStatus:
        return self._sensorstatus

    @property
    def battery_status(self) -> str:
        return self._battery_status

    @property
    def sensorstate(self) -> str:
        return self._sensorstate

    @property
    def sensortype(self) -> ZoneSensorType:
        return self._sensortype

    @property
    def zone_id(self) -> str:
        return self._zone_id

    @property
    def zone_type(self) -> str:
        return self._zone_type

    @property
    def zone_physical_type(self) -> str:
        return self._zone_physical_type

    @property
    def zone_alarm_type(self) -> str:
        return self._zone_alarm_type

    @property
    def partition_id(self) -> str:
        return self._partition_id

    @property
    def shortID(self) -> str:
        return self._shortID

    @property
    def time(self) -> str:
        return self._time

    @property
    def current_capability(self) -> str:
        return self._current_capability

    @property
    def latestdBm(self) -> int | None:
        try:
            n = int(self._latestdBm)
            if n >= 0 and n < 999:  # noqa: PLR2004
                return n
        except ValueError:
            pass
        return None

    @property
    def averagedBm(self) -> int | None:
        try:
            n = int(self._averagedBm)
            if n >= 0 and n < 999:  # noqa: PLR2004
                return n
        except ValueError:
            pass
        return None

    @property
    def device_capability(self) -> str:
        return self._device_capability

    @property
    def ac_status(self) -> str:
        return self._ac_status

    @property
    def powerg_temperature(self) -> float | None:
        return self._powerg_temperature

    @property
    def powerg_light(self) -> float | None:
        return self._powerg_light

    @property
    def powerg_status_data(self) -> str:
        return self._powerg_status_data

    @powerg_temperature.setter
    def powerg_temperature(self, value: str) -> None:
        if self._powerg_temperature != value:
                LOGGER.debug("Zone%s (%s) - powerg_temperature: %s", self._zone_id, self.sensorname, value)
                self._powerg_temperature = value
                self.notify()

    @powerg_light.setter
    def powerg_light(self, value: str) -> None:
        if self._powerg_light != value:
            LOGGER.debug("Zone%s (%s) - powerg_light: %s", self._zone_id, self.sensorname, value)
            self._powerg_light = value
            self.notify()

    @powerg_status_data.setter
    def powerg_status_data(self, value: str) -> None:
        if self._powerg_status_data != value:
            LOGGER.debug("Zone%s (%s) - powerg_status_data: %s", self._zone_id, self.sensorname, value)
            self._powerg_status_data = value
            self.notify()

    @averagedBm.setter
    def averagedBm(self, value: str) -> None:
        if self._averagedBm != value:
            self._averagedBm = value
            self.notify()

    @latestdBm.setter
    def latestdBm(self, value: str) -> None:
        if self._latestdBm != value:
            self.latestdBm = value
            self.notify()

    @sensorstatus.setter
    def sensorstatus(self, new_value: ZoneStatus) -> None:
        if self._settings.motion_sensor_delay and self._sensortype in {ZoneSensorType.MOTION, ZoneSensorType.PANEL_MOTION}:
            if new_value == ZoneStatus.IDLE:
                return
            if self._delay_task is not None:
                self._delay_task.cancel()
            self._delay_task = asyncio.create_task(self.delay_zone(ZoneStatus.IDLE))

        if self._sensorstatus != new_value:
            LOGGER.debug("Zone%s (%s) - sensorstatus: %s", self._zone_id, self.sensorname, new_value)
            self._sensorstatus = new_value
            self.notify()

    async def delay_zone(self,next_status: ZoneStatus) -> None:
        await asyncio.sleep(self._settings.motion_sensor_delay_sec)
        self._sensorstatus = next_status
        LOGGER.debug("Zone%s (%s) - sensorstatus: %s", self._zone_id, self.sensorname, next_status)
        self.notify()

    @battery_status.setter
    def battery_status(self, value: str) -> None:
        if self._battery_status != value:
            LOGGER.debug("Zone%s (%s) - battery_status: %s", self.zone_id, self.sensorname, value)
            self._battery_status = value
            self.notify()

    @sensorname.setter
    def sensorname(self, value: str) -> None:
        if self.sensorname != value:
            self._sensorname = value
            self.notify()

    @time.setter
    def time(self, value: str) -> None:
        if self._time != value:
            self._time = value
            self.notify()

    @sensortype.setter
    def sensortype(self, value: ZoneSensorType) -> None:
        if self._sensortype != value:
            self._sensortype = value
            self.notify()

    @sensorgroup.setter
    def sensorgroup(self, new_value: str) -> None:
        if self._sensorgroup != new_value:

            # Report new values
            try:
                ZoneSensorGroup(new_value)
            except ValueError:
                LOGGER.exception("Unknown Sensor group: %s, please report", new_value)

            self._sensorgroup = new_value
            LOGGER.debug("Zone%s (%s) - sensorgroup: %s", self.zone_id, self.sensorname, new_value)
            self.notify()

    @partition_id.setter
    def partition_id(self, value: str) -> None:
        if self.partition_id != value:
            self.partition_id = value
            self.notify()

    def to_powerg_dict(self) -> dict:
        return {
            "shortID": self.shortID,
            "longID": self._powerg_long_id,
            "status_data": self._powerg_status_data,
            "temperature": self._powerg_temperature,
            "light": self._powerg_light,
            "notification_period": self._powerg_notification_period,
            "average_link_quality": self._powerg_average_link_quality,
            "link_quality": self._powerg_link_quality,
            "link_status": self._powerg_link_status,
            "battery_voltage": self._powerg_battery_voltage,
        }

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "ac_status": self.ac_status,
            "allowdisarming": self._allowdisarming,
            "averagedBm": self.averagedBm,
            "battery_status": self.battery_status,
            "chimetype": self._chimetype,
            "created_by": self._created_by,
            "created_date": self._created_date,
            "current_capability": self._current_capability,
            "device_capability": self._device_capability,
            "diag_24hr": self._diag_24hr,
            "extras": self._extras,
            "sensorid": self._sensor_id,
            "sensorname": self.sensorname,
            "sensorgroup": self.sensorgroup,
            "sensorstatus": self.sensorstatus.value,
            "sensorstate": self.sensorstate,
            "sensortype": self.sensortype.value,
            "zoneid": self.zone_id,
            "zone_type": self.zone_type,
            "zone_physical_type": self.zone_physical_type,
            "zone_alarm_type": self.zone_alarm_type,
            "partition_id": self.partition_id,
            "sensortts": self._sensortts,
            "latestdBm": self.latestdBm,
            "zone_rf_sensor": self._zone_rf_sensor,
            "zone_supervised": self._zone_supervised,
            "zone_reporting_enabled": self._zone_reporting_enabled,
            "zone_two_way_voice_enabled": self._zone_two_way_voice_enabled,
            "signal_source": self._signal_source,
            "serial_number": self._serial_number,
            "frame_count": self._frame_count,
            "frame_type": self._frame_type,
            "frame_id": self._frame_id,
            "time": self.time,
            "version": self._version,
            "opr": self._opr,
            "zone_equipment_code": self._zone_equipement_code,
            "updated_by": self._updated_by,
            "updated_date": self._updated_date,
            "shortID": self._shortID,
            "sub_type": self._sub_type,
            "powerg_manufacture_id": self._powerg_manufacture_id,
            "parent_node": self._parent_node,
        }
