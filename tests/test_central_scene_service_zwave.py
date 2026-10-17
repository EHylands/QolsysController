"""Tests for CentralSceneServiceZwave scene discovery and event emission."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_central_scene import CentralSceneServiceZwave

from .zwave_service_helpers import make_zwave_device


def _make(endpoint: int = 0) -> tuple[CentralSceneServiceZwave, MagicMock]:
    device = make_zwave_device()
    return CentralSceneServiceZwave(automation_device=device, endpoint=endpoint), device


class TestCentralSceneServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "CentralSceneService"

    def test_set_supported_discovers_scene(self) -> None:
        service, _ = _make()
        service.set_supported(1, ["single_tap", "double_tap"])
        assert 1 in service.scenes
        assert service.scenes[1].supported == ["single_tap", "double_tap"]

    def test_emit_scene_event_records_last_event_and_notifies(self) -> None:
        service, device = _make()
        service.set_supported(1, ["single_tap"])
        service.emit_scene_event(1, "single_tap", sequence=5)
        assert service.scenes[1].last_event == "single_tap"
        device.notify.assert_called_once()

    def test_emit_scene_event_for_unknown_scene_is_ignored(self) -> None:
        service, device = _make()
        service.emit_scene_event(9, "single_tap", sequence=1)
        assert 9 not in service.scenes
        device.notify.assert_not_called()

    def test_duplicate_sequence_is_dropped(self) -> None:
        service, _ = _make()
        service.set_supported(1, ["single_tap", "double_tap"])
        service.emit_scene_event(1, "single_tap", sequence=5)
        # Same sequence number -> treated as an RF retransmission and ignored.
        service.emit_scene_event(1, "double_tap", sequence=5)
        assert service.scenes[1].last_event == "single_tap"
