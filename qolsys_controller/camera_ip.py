from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from qolsys_controller.enum_qolsys import QolsysNotification
from qolsys_controller.observable import Event, QolsysObservable

LOGGER = logging.getLogger(__name__)


class QolsysIpCamera(QolsysObservable):
    def __init__(self, camera_id: str = "", camera_name: str = "") -> None:
        super().__init__()
        self._camera_id: str = camera_id
        self._camera_name: str = camera_name
        self._lastupdate: datetime | None = None

    def update_event(self, data: dict[str, Any]) -> None:
        camera_id = data.get("cameraId")
        if camera_id != self._camera_id:
            LOGGER.debug("QolsysIpCamera[%s] - ignoring event for camera_id: %s", self._camera_id, camera_id)
            return

        self._camera_name = data.get("cameraName", self._camera_name)
        self._lastupdate = datetime.now(timezone.utc)

        event_type = data.get("eventType")
        match event_type:
            case 1:
                LOGGER.debug("QolsysIpCamera[%s] - %s - Press Event", self._camera_id, self._camera_name)
                self.notify(Event(QolsysNotification.CAMERA_PRESS_EVENT, self, self.to_dict_event()))
            case 2:
                LOGGER.debug("QolsysIpCamera[%s] - %s - Motion Event", self._camera_id, self._camera_name)
                self.notify(Event(QolsysNotification.CAMERA_MOTION_EVENT, self, self.to_dict_event()))
            case _:
                LOGGER.debug("QolsysIpCamera[%s] - %s - Unknown Event: %s", self._camera_id, self._camera_name, event_type)

    def update_camera(self, data: dict[str, Any]) -> None:
        camera_id = data.get("camera_id", "")
        if camera_id != self._camera_id:
            LOGGER.error(
                "Updating IpCamera%s (%s) with IpCamera%s (different id)", self._camera_id, self._camera_name, camera_id
            )
            return

        if "camera_name" in data:
            self.camera_name = data.get("camera_name", "")

    def to_dict(self) -> dict[str, str]:
        return {
            "camera_id": self._camera_id,
            "camera_name": self._camera_name,
            "lastupdate": str(self._lastupdate),
        }

    def to_dict_event(self) -> dict[str, Any]:
        return {
            "camera_id": self._camera_id,
            "camera_name": self._camera_name,
            "lastupdate": str(self._lastupdate),
        }

    # -----------------------------
    # properties
    # -----------------------------

    @property
    def camera_id(self) -> str:
        return self._camera_id

    @property
    def camera_name(self) -> str:
        return self._camera_name

    @camera_name.setter
    def camera_name(self, value: str) -> None:
        if self._camera_name != value:
            LOGGER.debug("QolsysIpCamera[%s] - camera_name: %s -> %s", self._camera_id, self._camera_name, value)
            self._camera_name = value

    @property
    def lastupdate(self) -> datetime | None:
        return self._lastupdate
