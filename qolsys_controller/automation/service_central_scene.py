from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from qolsys_controller.automation.service import AutomationService
from qolsys_controller.enum_qolsys import QolsysNotification
from qolsys_controller.observable import Event

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class CentralScene:
    """A single scene (button) on a Central Scene endpoint.

    ``supported`` is the list of event names the scene can emit (single_tap,
    double_tap, hold, release, ...). For Z-Wave it is loaded from the panel's
    central_scene_supported field; it stays empty until that field is parsed.
    """

    def __init__(self, scene_number: int) -> None:
        self.scene_number: int = scene_number
        self.supported: list[str] = []
        self.last_event: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "supported": self.supported,
            "last_event": self.last_event,
        }


class CentralSceneService(AutomationService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "CentralSceneService"
        # scene_number -> CentralScene, discovered from the panel's central_scene_supported field.
        self._scenes: dict[int, CentralScene] = {}
        self._last_sequence: int | None = None

    @property
    def scenes(self) -> dict[int, CentralScene]:
        return self._scenes

    def set_supported(self, scene: int, supported: list[str]) -> None:
        """Discover a scene and set the key attributes it supports (loaded from central_scene_supported)."""
        central_scene = self._scenes.get(scene)
        if central_scene is None:
            central_scene = CentralScene(scene)
            self._scenes[scene] = central_scene
            LOGGER.debug("%s - discovered scene %s (supported: %s)", self.prefix, scene, supported)
        central_scene.supported = supported

    def emit_scene_event(self, scene: int, event: str, sequence: int | None = None) -> None:
        """Propagate a stateless scene event (single_tap, double_tap, hold, ...).

        Edge triggered: fires AUTOMATION_CENTRAL_SCENE_EVENT on every notification so
        repeated identical presses each reach Home Assistant. The scene must have
        been discovered first (via set_supported); unknown scenes are ignored.
        Duplicate RF retransmissions are dropped using the sequence number only.
        """
        central_scene = self._scenes.get(scene)
        if central_scene is None:
            return

        if sequence is not None and sequence == self._last_sequence:
            LOGGER.debug("%s - dropping duplicate scene event (sequence %s)", self.prefix, sequence)
            return
        self._last_sequence = sequence

        central_scene.last_event = event
        LOGGER.debug("%s - scene %s: %s", self.prefix, scene, event)
        self.automation_device.notify(
            Event(
                QolsysNotification.AUTOMATION_CENTRAL_SCENE_EVENT,
                self.automation_device,
                self.to_dict_scene_event(scene, event),
            )
        )

    def update_automation_service(self) -> None:
        pass

    def info(self) -> list[str]:
        return [
            f"{self.prefix} - scene {scene}: {central_scene.supported}"
            for scene, central_scene in sorted(self._scenes.items())
        ]

    def to_dict_scene_event(self, scene: int, event: str) -> dict[str, Any]:
        return {
            "service_type": self.service_name,
            "virtual_node_id": self.automation_device.virtual_node_id,
            "endpoint": self.endpoint,
            "scene_number": scene,
            "event": event,
            "sequence": self._last_sequence,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def to_dict_event(self) -> dict[str, Any]:
        return {
            "service_type": self.service_name,
            "state": {
                "scenes": {scene: central_scene.to_dict() for scene, central_scene in self._scenes.items()},
            },
            "attributes": {
                "endpoint": self.endpoint,
            },
            "capabilities": {},
        }
