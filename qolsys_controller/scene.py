import logging

from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)


class QolsysScene(QolsysObservable):

    def __init__(self, data: dict) -> None:
        super().__init__()

        self._scene_id = data.get("scene_id", "")
        self._name = data.get("name", "")
        self._icon = data.get("icon", "")
        self._color = data.get("color", "")

    def update(self, data: dict) -> None:

        scene_id_update = data.get("scene_id", "")
        if scene_id_update != self._scene_id:
            LOGGER.error("Updating Scene%s (%s) with Scene%s (different id)", self._scene_id, self.sensorname, scene_id_update)
            return

        self.start_batch_update()

        # Update name
        if "name" in data:
            self.sensorname = data.get("name")

        if "color" in data:
            self.color = data.get("color")

        if "icon" in data:
            self.icon = data.get("icon")

        self.end_batch_update()

    @property
    def scene_id(self) -> str:
        return self._scene_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def color(self) -> str:
        return self._color

    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            self._name = value
            self.notify()

    @icon.setter
    def icon(self, value: str) -> None:
        if self._icon != value:
            self._icon = value
            self.notify()

    @color.setter
    def color(self, value: str) -> None:
        if self._color != value:
            self._color = value
            self.notify()

    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "color": self.color,
            "icon": self.icon,
        }
