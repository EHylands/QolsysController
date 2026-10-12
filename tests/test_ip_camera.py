"""Tests for parsing the panel's IP_CAMERA_LIST setting into QolsysIpCamera objects."""

from __future__ import annotations

from unittest.mock import MagicMock

from qolsys_controller.panel import QolsysPanel

IP_CAMERA_LIST = """[{"cameraId":"06A8F508-0800","name":"Backyard"},
 {"cameraId":"06A8F508-0802","name":"Doorbell"},
 {"cameraId":"06A8F508-0801","name":"Driveway"},
 {"cameraId":"06A8F508-0803","name":"Veranda"}]"""


def _make_panel(ip_camera_list: str) -> QolsysPanel:
    panel = QolsysPanel(MagicMock())
    panel._db = MagicMock()
    panel._db.get_setting_panel.return_value = ip_camera_list
    return panel


def test_parses_all_cameras_from_settings() -> None:
    panel = _make_panel(IP_CAMERA_LIST)
    cameras = panel.get_ip_camera_list_from_settings()
    assert [(camera.camera_id, camera.camera_name) for camera in cameras] == [
        ("06A8F508-0800", "Backyard"),
        ("06A8F508-0802", "Doorbell"),
        ("06A8F508-0801", "Driveway"),
        ("06A8F508-0803", "Veranda"),
    ]


def test_empty_setting_returns_no_cameras() -> None:
    assert _make_panel("").get_ip_camera_list_from_settings() == []


def test_malformed_json_returns_no_cameras() -> None:
    assert _make_panel("not json").get_ip_camera_list_from_settings() == []


def test_non_list_payload_returns_no_cameras() -> None:
    assert _make_panel('{"cameraId":"06A8F508-0800","name":"Backyard"}').get_ip_camera_list_from_settings() == []


def test_entries_without_camera_id_are_skipped() -> None:
    panel = _make_panel('[{"name":"No Id"}, {"cameraId":"06A8F508-0800","name":"Backyard"}]')
    cameras = panel.get_ip_camera_list_from_settings()
    assert [(camera.camera_id, camera.camera_name) for camera in cameras] == [("06A8F508-0800", "Backyard")]
