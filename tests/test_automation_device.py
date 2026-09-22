"""Tests for the automation device hierarchy.

Covers the base ``QolsysAutomationDevice`` (service registry + the endpoint
guard) and the ``ADC``, ``Z-Wave`` and ``Zigbee`` subclasses.

Regression focus: ``int(self.end_point)`` used to raise ``ValueError`` when
``end_point`` was an empty string, silently dropping services on ADC devices
(no endpoint) and crashing the Z-Wave constructor for devices discovered
outside the automation content provider (empty ``dev_dict``).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from qolsys_controller.automation.device import QolsysAutomationDevice
from qolsys_controller.automation.service_central_scene import CentralSceneService
from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC
from qolsys_controller.automation_adc.service_cover import CoverServiceADC
from qolsys_controller.automation_adc.service_light import LightServiceADC
from qolsys_controller.automation_adc.service_status import StatusServiceADC
from qolsys_controller.automation_zigbee.device import QolsysAutomationDeviceZigbee
from qolsys_controller.automation_zigbee.service_battery import BatteryServiceZigbee
from qolsys_controller.automation_zigbee.service_status import StatusServiceZigbee
from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave
from qolsys_controller.automation_zwave.service_battery import BatteryServiceZwave
from qolsys_controller.automation_zwave.service_central_scene import CentralSceneServiceZwave
from qolsys_controller.automation_zwave.service_light import LightServiceZwave
from qolsys_controller.automation_zwave.service_status import StatusServiceZwave
from qolsys_controller.enum_qolsys import AutomationDeviceProtocol, QolsysNotification
from qolsys_controller.enum_zwave import ZwaveCommandClass


class _Device(QolsysAutomationDevice):
    """Minimal concrete device used to exercise base-class behavior."""


def _make_base_device(**dev: str) -> _Device:
    dev_dict: dict[str, str] = {"virtual_node_id": "5", "protocol": "Z-Wave"}
    dev_dict.update(dev)
    return _Device(MagicMock(), dev_dict)


def _adc_func(
    func_id: int,
    func_name: str,
    func_type: int,
    func_state: int = 0,
    local_control: int = 2,
) -> dict[str, object]:
    return {
        "vdFuncId": func_id,
        "vdFuncLocalControl": local_control,
        "vdFuncName": func_name,
        "vdFuncType": func_type,
        "vdFuncState": func_state,
        "vdFuncBackendTimestamp": "ts",
    }


def _make_adc_device(func_list: list[dict[str, object]] | None = None, device_id: str = "42") -> QolsysAutomationDeviceADC:
    adc_dict: dict[str, str] = {"device_id": device_id, "name": "Garage"}
    if func_list is not None:
        adc_dict["func_list"] = json.dumps(func_list)
    return QolsysAutomationDeviceADC(MagicMock(), adc_dict)


class TestServiceRegistry:
    def test_add_and_get_roundtrip(self) -> None:
        device = _make_base_device()
        device.service_add_status_service(endpoint=0)
        assert device.service_get(StatusServiceZwave, 0) is not None

    def test_duplicate_service_rejected(self) -> None:
        device = _make_base_device()
        device.service_add_status_service(endpoint=0)
        device.service_add_status_service(endpoint=0)
        assert len(device.services[0]) == 1

    def test_unknown_service_not_added(self) -> None:
        device = _make_base_device()
        device.service_add(MagicMock())  # not one of the known service types
        assert device.services == {}

    def test_get_returns_none_when_absent(self) -> None:
        device = _make_base_device()
        assert device.service_get(StatusServiceZwave, 0) is None


class TestProtocolProperty:
    def test_known_protocol(self) -> None:
        device = _make_base_device(protocol="Zigbee")
        assert device.protocol is AutomationDeviceProtocol.ZIGBEE

    def test_unknown_protocol_falls_back(self) -> None:
        device = _make_base_device(protocol="carrier-pigeon")
        assert device.protocol is AutomationDeviceProtocol.UNKNOWN


class TestUpdateAutomationDevice:
    def test_wrong_node_ignored(self) -> None:
        device = _make_base_device(virtual_node_id="5", device_name="Kitchen")
        device.update_automation_device({"virtual_node_id": "99", "device_name": "Hacked"})
        assert device.device_name == "Kitchen"

    def test_applies_fields(self) -> None:
        device = _make_base_device(virtual_node_id="5", device_name="Kitchen", status="off")
        device.update_automation_device({"virtual_node_id": "5", "device_name": "Hallway", "status": "on"})
        assert device.device_name == "Hallway"
        assert device.status == "on"


class TestEndpointGuard:
    """Regression tests for the empty/non-numeric ``end_point`` guard."""

    def test_service_added_when_endpoint_empty(self) -> None:
        # ADC devices have no end_point; the cover service must still be added.
        device = _make_base_device(protocol="ADC", end_point="")
        device.service_add_cover_service(endpoint=1)
        assert device.service_get(CoverServiceADC, 1) is not None

    def test_not_main_endpoint_when_endpoint_empty(self) -> None:
        device = _make_base_device(protocol="Z-Wave", end_point="")
        device.service_add_status_service(endpoint=0)
        service = device.service_get(StatusServiceZwave, 0)
        assert service is not None
        assert service.is_main_endpoint_service is False

    def test_main_endpoint_when_endpoint_matches(self) -> None:
        device = _make_base_device(protocol="Z-Wave", end_point="0")
        device.service_add_status_service(endpoint=0)
        service = device.service_get(StatusServiceZwave, 0)
        assert service is not None
        assert service.is_main_endpoint_service is True

    def test_init_dispatch_non_numeric_endpoint_does_not_raise(self) -> None:
        # Constructor dispatch for "Light" must not raise on an empty end_point.
        device = _make_base_device(protocol="Z-Wave", device_type="Light", end_point="")
        assert device.service_get(LightServiceZwave, 0) is not None


class TestADCDevice:
    def test_garage_door_adds_cover_service(self) -> None:
        device = _make_adc_device([_adc_func(1, "Open/Close", 1)])
        assert device.service_get(CoverServiceADC, 1) is not None

    def test_light_adds_light_service(self) -> None:
        device = _make_adc_device([_adc_func(2, "Off/On", 3)])
        assert device.service_get(LightServiceADC, 2) is not None

    def test_malfunction_adds_status_service(self) -> None:
        device = _make_adc_device([_adc_func(3, "Malfunction", 10)])
        assert device.service_get(StatusServiceADC, 3) is not None

    def test_invalid_func_entry_skipped_others_added(self) -> None:
        # A bogus vdFuncName raises inside the loop; the valid entry still lands.
        device = _make_adc_device(
            [
                _adc_func(1, "Open/Close", 1),
                _adc_func(2, "Bogus-Name", 1),
            ]
        )
        assert device.service_get(CoverServiceADC, 1) is not None
        assert device.service_get(CoverServiceADC, 2) is None

    def test_empty_func_list_adds_no_services(self) -> None:
        device = _make_adc_device()
        assert device.services == {}

    def test_protocol_is_adc(self) -> None:
        device = _make_adc_device()
        assert device.protocol is AutomationDeviceProtocol.ADC

    def test_update_wrong_node_ignored(self) -> None:
        device = _make_adc_device(device_id="42")
        device.update_adc_device({"device_id": "999", "name": "Hacked"})
        assert device.device_name == "Garage"

    def test_update_applies_name(self) -> None:
        device = _make_adc_device(device_id="42")
        device.update_adc_device({"device_id": "42", "name": "Shed Door"})
        assert device.device_name == "Shed Door"

    def test_func_list_stored_in_to_dict(self) -> None:
        func_list = [_adc_func(1, "Open/Close", 1)]
        device = _make_adc_device(func_list)
        assert json.loads(device.to_dict_adc()["func_list"]) == func_list


class TestZigbeeDevice:
    def _make(self, **dev: str) -> QolsysAutomationDeviceZigbee:
        dev_dict: dict[str, str] = {"virtual_node_id": "7", "protocol": "Zigbee", "device_name": "ZbSensor"}
        dev_dict.update(dev)
        return QolsysAutomationDeviceZigbee(MagicMock(), dev_dict)

    def test_base_services_added(self) -> None:
        device = self._make()
        assert device.service_get(StatusServiceZigbee, 0) is not None
        assert device.service_get(BatteryServiceZigbee, 0) is not None

    def test_protocol_is_zigbee(self) -> None:
        assert self._make().protocol is AutomationDeviceProtocol.ZIGBEE


class TestZwaveDevice:
    def _make(self, zwave: dict[str, str] | None = None, dev: dict[str, str] | None = None) -> QolsysAutomationDeviceZwave:
        return QolsysAutomationDeviceZwave(MagicMock(), zwave or {"node_id": "8"}, dev or {})

    def test_empty_dev_dict_does_not_raise(self) -> None:
        # panel.py builds Z-Wave devices with an empty dev_dict (no end_point).
        device = self._make()
        assert device.service_get(StatusServiceZwave, 0) is not None
        assert device.service_get(BatteryServiceZwave, 0) is not None

    def test_numeric_endpoint_marks_main_service(self) -> None:
        device = self._make(dev={"virtual_node_id": "9", "end_point": "0"})
        service = device.service_get(StatusServiceZwave, 0)
        assert service is not None
        assert service.is_main_endpoint_service is True

    def test_protocol_is_zwave(self) -> None:
        assert self._make().protocol is AutomationDeviceProtocol.ZWAVE

    def test_command_class_list_parsing(self) -> None:
        token = int(ZwaveCommandClass.SwitchBinary)
        device = self._make(zwave={"node_id": "8", "command_class_list": f"[{token},not-a-number]"})
        # Valid tokens parse; garbage tokens are skipped rather than raising.
        assert ZwaveCommandClass.SwitchBinary in device.command_class_list


class TestCentralScene:
    """CentralScene is discovered via multi_channel_details and queried in zwave_report."""

    _CS = int(ZwaveCommandClass.CentralScene)

    def _make_zwave(
        self,
        endpoint_command_classes: dict[int, list[int]],
        command_class_list: str | None = None,
    ) -> tuple[QolsysAutomationDeviceZwave, MagicMock]:
        controller = MagicMock()
        controller.commands.zwave.central_scene_supported_get = AsyncMock(return_value={})
        zwave_dict = {
            "node_id": "8",
            "multi_channel_details": json.dumps({str(ep): cc for ep, cc in endpoint_command_classes.items()}),
            "command_class_list": command_class_list if command_class_list is not None else f"[{self._CS}]",
        }
        device = QolsysAutomationDeviceZwave(controller, zwave_dict, {"virtual_node_id": "8", "end_point": "0"})
        return device, controller

    def test_setter_adds_service_synchronously(self) -> None:
        device, controller = self._make_zwave({1: [self._CS]})
        assert isinstance(device.service_get(CentralSceneService, 1), CentralSceneServiceZwave)
        # The setter must not fire the async command (would leak a coroutine).
        controller.commands.zwave.central_scene_supported_get.assert_not_awaited()

    def test_setter_no_service_without_central_scene(self) -> None:
        device, _ = self._make_zwave({1: [int(ZwaveCommandClass.SwitchMultilevel)]}, command_class_list="[]")
        assert device.service_get(CentralSceneService, 0) is None
        assert device.service_get(CentralSceneService, 1) is None

    def test_root_central_scene_from_command_class_list(self) -> None:
        # A node advertising CentralScene at the root (endpoint 0) — e.g. a Zooz paddle
        # switch — gets a root service even without a multi_channel_details entry.
        device, _ = self._make_zwave({}, command_class_list=f"[{self._CS}]")
        assert isinstance(device.service_get(CentralSceneService, 0), CentralSceneServiceZwave)

    def test_setter_does_not_duplicate(self) -> None:
        device, _ = self._make_zwave({1: [self._CS]})
        device.multi_channel_details = json.dumps({"1": [self._CS], "2": [self._CS]})
        assert len(device.services[1]) == 1

    async def test_zwave_report_queries_each_endpoint(self) -> None:
        # command_class_list carries CentralScene, so the root (endpoint 0) also gets a
        # service, alongside the multi-channel endpoints 1 and 2.
        device, controller = self._make_zwave({1: [self._CS], 2: [self._CS]})
        await device.zwave_report()
        assert controller.commands.zwave.central_scene_supported_get.await_count == 3
        awaited = {c.args for c in controller.commands.zwave.central_scene_supported_get.await_args_list}
        assert awaited == {("8", "0"), ("8", "1"), ("8", "2")}

    async def test_zwave_report_skips_when_command_class_absent(self) -> None:
        # Service is present (from multi_channel_details) but the node doesn't list CentralScene.
        device, controller = self._make_zwave({1: [self._CS]}, command_class_list="[]")
        assert device.service_get(CentralSceneService, 1) is not None
        await device.zwave_report()
        controller.commands.zwave.central_scene_supported_get.assert_not_awaited()

    def test_base_device_add_central_scene_zwave(self) -> None:
        device = _make_base_device(protocol="Z-Wave")
        device.service_add_central_scene_service(endpoint=0)
        assert isinstance(device.service_get(CentralSceneService, 0), CentralSceneServiceZwave)

    def test_base_device_add_central_scene_non_zwave_is_noop(self) -> None:
        device = _make_base_device(protocol="ADC")
        device.service_add_central_scene_service(endpoint=0)
        assert device.service_get(CentralSceneService, 0) is None


class TestCentralSceneEvents:
    """Stateless scene events (single_tap, double_tap, hold, release, ...)."""

    _CS = int(ZwaveCommandClass.CentralScene)

    def _make_zwave_with_service(self) -> tuple[QolsysAutomationDeviceZwave, list[dict[str, Any]], list[dict[str, Any]]]:
        controller = MagicMock()
        controller.commands.zwave.central_scene_supported_get = AsyncMock(return_value={})
        zwave_dict = {
            "node_id": "8",
            "multi_channel_details": json.dumps({"1": [self._CS]}),
            "command_class_list": f"[{self._CS}]",
        }
        device = QolsysAutomationDeviceZwave(controller, zwave_dict, {"virtual_node_id": "8", "end_point": "0"})
        events: list[dict[str, Any]] = []
        adds: list[dict[str, Any]] = []
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_EVENT, lambda e: events.append(e.data))
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_ADD, lambda e: adds.append(e.data))
        return device, events, adds

    def _report(self, sequence: int, key_attribute: int, scene: int) -> bytes:
        return bytes([self._CS, 0x03, sequence, key_attribute, scene])

    def test_emit_scene_event_notifies(self) -> None:
        device = _make_base_device(protocol="Z-Wave")
        device.service_add_central_scene_service(endpoint=0)
        service = device.service_get(CentralSceneService, 0)
        assert service is not None

        events: list[dict[str, Any]] = []
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_EVENT, lambda e: events.append(e.data))
        service.emit_scene_event(1, "single_tap", sequence=5)

        assert len(events) == 1
        assert events[0]["event"] == "single_tap"
        assert events[0]["scene_number"] == 1
        assert events[0]["endpoint"] == 0
        assert service.scenes[1].last_event == "single_tap"

    def test_emit_dedupes_same_sequence(self) -> None:
        device = _make_base_device(protocol="Z-Wave")
        device.service_add_central_scene_service(endpoint=0)
        service = device.service_get(CentralSceneService, 0)
        assert service is not None

        events: list[dict[str, Any]] = []
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_EVENT, lambda e: events.append(e.data))
        service.emit_scene_event(1, "single_tap", sequence=5)
        service.emit_scene_event(1, "single_tap", sequence=5)  # duplicate RF frame
        service.emit_scene_event(1, "single_tap", sequence=6)  # new press

        assert len(events) == 2

    def test_update_raw_fires_event(self) -> None:
        device, events, _ = self._make_zwave_with_service()
        device.update_raw(self._report(sequence=1, key_attribute=0x03, scene=2), endpoint=1)
        assert len(events) == 1
        assert events[0]["event"] == "double_tap"
        assert events[0]["scene_number"] == 2

    def test_update_raw_maps_key_attributes(self) -> None:
        device, events, _ = self._make_zwave_with_service()
        expected = {0x00: "single_tap", 0x01: "release", 0x02: "hold", 0x03: "double_tap", 0x04: "triple_tap"}
        for seq, (key, name) in enumerate(expected.items()):
            device.update_raw(self._report(sequence=seq, key_attribute=key, scene=1), endpoint=1)
        assert [e["event"] for e in events] == list(expected.values())

    def test_update_raw_no_service_no_event(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        # endpoint 2 has no CentralScene service
        device.update_raw(self._report(sequence=1, key_attribute=0x00, scene=1), endpoint=2)
        assert events == []
        assert adds == []

    def test_update_raw_unknown_key_attribute_ignored(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        device.update_raw(self._report(sequence=1, key_attribute=0x07, scene=1), endpoint=1)
        assert events == []
        assert adds == []

    def test_new_scene_fires_add_before_event(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        order: list[str] = []
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_ADD, lambda e: order.append("add"))
        device.register(QolsysNotification.AUTOMATION_CENTRAL_SCENE_EVENT, lambda e: order.append("event"))

        device.update_raw(self._report(sequence=1, key_attribute=0x00, scene=5), endpoint=1)

        assert len(adds) == 1
        assert adds[0]["scene_number"] == 5
        assert adds[0]["endpoint"] == 1
        assert adds[0]["supported"] == []  # discovered by a press, before any Supported Report
        assert "event" not in adds[0]  # the add notification carries no key attribute
        assert order == ["add", "event"]  # entity must be created before the press lands

    def test_known_scene_does_not_readd(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        device.update_raw(self._report(sequence=1, key_attribute=0x00, scene=1), endpoint=1)
        device.update_raw(self._report(sequence=2, key_attribute=0x03, scene=1), endpoint=1)
        assert len(adds) == 1  # scene 1 added only once
        assert len(events) == 2

    def test_scenes_built_from_reports(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        device.update_raw(self._report(sequence=1, key_attribute=0x00, scene=1), endpoint=1)
        device.update_raw(self._report(sequence=2, key_attribute=0x00, scene=3), endpoint=1)
        service = device.service_get(CentralSceneService, 1)
        assert service is not None
        assert sorted(service.scenes) == [1, 3]
        assert {a["scene_number"] for a in adds} == {1, 3}

    def _supported_report(self, supported_scenes: int, properties: int, *bitmasks: int) -> bytes:
        return bytes([self._CS, 0x02, supported_scenes, properties, *bitmasks])

    def test_supported_report_populates_per_scene(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        # properties 0x02 -> identical=0, 1 bitmask byte per scene.
        # scene 1 mask 0x09 = bit0 (single_tap) + bit3 (double_tap); scene 2 mask 0x04 = bit2 (hold).
        device.update_raw(self._supported_report(2, 0x02, 0x09, 0x04), endpoint=1)

        service = device.service_get(CentralSceneService, 1)
        assert service is not None
        assert sorted(service.scenes) == [1, 2]
        assert service.scenes[1].supported == ["single_tap", "double_tap"]
        assert service.scenes[2].supported == ["hold"]
        # A Supported Report discovers scenes (fires ADD with the supported list) but is not a press.
        assert {a["scene_number"] for a in adds} == {1, 2}
        assert adds[0]["supported"] == ["single_tap", "double_tap"]
        assert events == []

    def test_supported_report_identical_applies_to_all_scenes(self) -> None:
        device, events, adds = self._make_zwave_with_service()
        # properties 0x03 -> identical=1, 1 bitmask byte; single mask 0x05 = bit0 (single_tap) + bit2 (hold).
        device.update_raw(self._supported_report(3, 0x03, 0x05), endpoint=1)

        service = device.service_get(CentralSceneService, 1)
        assert service is not None
        assert sorted(service.scenes) == [1, 2, 3]
        for scene in (1, 2, 3):
            assert service.scenes[scene].supported == ["single_tap", "hold"]
