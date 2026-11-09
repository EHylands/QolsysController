"""MQTT QoS defaults and the publish timeout applied when QoS 1 is opted into."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import aiomqtt
import pytest

from qolsys_controller.controller import QolsysController
from qolsys_controller.errors import QolsysConfigError, QolsysMqttError


def test_mqtt_qos_defaults_to_zero() -> None:
    assert QolsysController().settings.mqtt_qos == 0


@pytest.mark.parametrize("qos", [0, 1, 2])
def test_mqtt_qos_accepts_valid_levels(qos: int) -> None:
    settings = QolsysController().settings

    settings.mqtt_qos = qos

    assert settings.mqtt_qos == qos


@pytest.mark.parametrize("qos", [-1, 3, "1", 1.0, True, None])
def test_mqtt_qos_rejects_invalid_values(qos: Any) -> None:
    settings = QolsysController().settings

    with pytest.raises(QolsysConfigError):
        settings.mqtt_qos = qos

    assert settings.mqtt_qos == 0


async def test_panel_subscriptions_use_configured_qos() -> None:
    controller = QolsysController()
    controller.settings.mqtt_qos = 1
    controller.settings.log_mqtt_messages = True
    controller._is_configured = True
    cast("Any", controller).notify_panel_status_update = lambda: None

    subscriptions: dict[str, int] = {}

    async def subscribe(topic: str, qos: int = 0) -> None:
        subscriptions[topic] = qos
        if topic == "mastermeid":  # Last subscription: end the session here
            raise aiomqtt.MqttError("stop")

    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.subscribe = subscribe
    cast("Any", controller).mqtt_open_transport_task = AsyncMock(return_value=client)

    with pytest.raises((QolsysMqttError, ExceptionGroup)):
        await controller.run_supervised(reconnect=False)

    assert "iq2meid" in subscriptions
    assert set(subscriptions.values()) == {1}


async def test_publish_uses_configured_command_timeout() -> None:
    controller = QolsysController()
    controller.settings.mqtt_command_timeout = 45
    client = SimpleNamespace(publish=AsyncMock())
    command = SimpleNamespace(_payload={"eventName": "ping"}, _topic="mastermeid", _qos=1)
    controller._mqtt_publish_queue.put_nowait(cast("Any", command))

    task = asyncio.create_task(controller.mqtt_publish_task(cast("Any", client)))
    while not client.publish.await_count:
        await asyncio.sleep(0)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    args, kwargs = client.publish.await_args
    assert args[0] == "mastermeid"
    assert args[2] == 1
    assert kwargs["timeout"] == 45
