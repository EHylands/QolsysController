"""Fatal supervisor errors must leave the controller stopped and report it offline."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import aiomqtt
import pytest

from qolsys_controller.controller import QolsysController
from qolsys_controller.enum_qolsys import ControllerState
from qolsys_controller.mqtt_bridge.client import MqttBridgeClient


def make_controller(*states: ControllerState) -> tuple[QolsysController, list[tuple[ControllerState, bool]]]:
    """Build a real controller whose supervisor walks `states`, then fails."""
    controller = QolsysController()
    controller.settings.mqtt_bridge_enabled = False
    events: list[tuple[ControllerState, bool]] = []

    def record() -> None:
        events.append((controller.controller_state, controller.controller_state == ControllerState.CONNECTED))

    async def failing_supervisor(reconnect: bool = True, start_pairing: bool = False) -> None:
        for state in states:
            await controller.set_controller_state(state)
        await asyncio.sleep(0)
        raise KeyError("boom")

    cast("Any", controller).notify_panel_status_update = record
    cast("Any", controller).run_supervised = failing_supervisor
    return controller, events


async def test_fatal_error_while_connected_reports_offline() -> None:
    controller, events = make_controller(ControllerState.CONNECTING, ControllerState.CONNECTED)

    with pytest.raises(KeyError):
        await controller.run_forever()

    assert events == [(ControllerState.CONNECTED, True), (ControllerState.SHUTTING_DOWN, False)]
    assert controller.controller_state == ControllerState.STOPPED
    assert controller._shutdown_complete.is_set()


async def test_controller_can_restart_after_fatal_error() -> None:
    controller, _ = make_controller(ControllerState.CONNECTING, ControllerState.CONNECTED)

    with pytest.raises(KeyError):
        await controller.run_forever()

    await controller.set_controller_state(ControllerState.CONFIGURING)
    assert controller.controller_state == ControllerState.CONFIGURING


async def test_fatal_error_before_connected_still_stops() -> None:
    controller = QolsysController()
    controller.settings.mqtt_bridge_enabled = False
    await controller.set_controller_state(ControllerState.CONNECTING)

    async def failing_supervisor(reconnect: bool = True, start_pairing: bool = False) -> None:
        raise KeyError("boom")

    cast("Any", controller).notify_panel_status_update = lambda: None
    cast("Any", controller).run_supervised = failing_supervisor

    with pytest.raises(KeyError):
        await controller.run_forever()

    assert controller.controller_state == ControllerState.STOPPED


def break_status_event(controller: QolsysController) -> None:
    def raise_db_error() -> dict[str, Any]:
        raise sqlite3.OperationalError("database is locked")

    cast("Any", controller)._to_event_dict = raise_db_error


async def test_status_event_failure_does_not_abort_transition() -> None:
    controller = QolsysController()
    await controller.set_controller_state(ControllerState.CONNECTING)
    break_status_event(controller)

    await controller.set_controller_state(ControllerState.CONNECTED)

    assert controller.controller_state == ControllerState.CONNECTED


async def test_status_events_only_fire_when_connected_changes() -> None:
    controller = QolsysController()
    events: list[ControllerState] = []
    cast("Any", controller).notify_panel_status_update = lambda: events.append(controller.controller_state)

    for state in (
        ControllerState.CONFIGURING,
        ControllerState.CONNECTING,
        ControllerState.CONNECTED,
        ControllerState.RECONNECTING,
        ControllerState.CONNECTING,
        ControllerState.RECONNECTING,
        ControllerState.CONNECTING,
        ControllerState.CONNECTED,
        ControllerState.SHUTTING_DOWN,
        ControllerState.STOPPED,
    ):
        await controller.set_controller_state(state)

    assert events == [
        ControllerState.CONNECTED,
        ControllerState.RECONNECTING,
        ControllerState.CONNECTED,
        ControllerState.SHUTTING_DOWN,
    ]


async def test_status_event_failure_does_not_block_shutdown() -> None:
    controller, _ = make_controller(ControllerState.CONNECTING, ControllerState.CONNECTED)
    del cast("Any", controller).notify_panel_status_update
    break_status_event(controller)

    with pytest.raises(KeyError):
        await controller.run_forever()

    assert controller.controller_state == ControllerState.STOPPED
    assert controller._shutdown_complete.is_set()


def make_bridge_client() -> MqttBridgeClient:
    # controller_state still reads CONNECTED when the bridge is cancelled.
    controller = SimpleNamespace(_to_event_dict=lambda: {"connected": True, "panel_ip": "10.0.0.2"})
    bridge = SimpleNamespace(_controller=controller, status_topic="base/panel/status", mqtt_qos=1)
    return MqttBridgeClient(cast("Any", bridge))


async def test_bridge_publishes_retained_offline_status() -> None:
    mqtt_client = SimpleNamespace(publish=AsyncMock())

    await make_bridge_client()._publish_offline_status(cast("Any", mqtt_client))

    args, kwargs = mqtt_client.publish.await_args
    assert args[0] == "base/panel/status"
    assert json.loads(args[1]) == {"connected": False, "panel_ip": "10.0.0.2"}
    assert kwargs["retain"] is True


async def test_bridge_offline_status_failure_is_swallowed() -> None:
    mqtt_client = SimpleNamespace(publish=AsyncMock(side_effect=aiomqtt.MqttError("gone")))

    await make_bridge_client()._publish_offline_status(cast("Any", mqtt_client))

    mqtt_client.publish.assert_awaited_once()
