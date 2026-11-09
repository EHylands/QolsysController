"""The periodic Z-Wave meter refresh must survive failures and device list changes."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave
from qolsys_controller.automation_zwave.service_meter import MeterServiceZwave
from qolsys_controller.controller import QolsysController
from qolsys_controller.enum_qolsys import ControllerState
from qolsys_controller.errors import QolsysOperationTimeoutError


def make_device(name: str, refresh: AsyncMock) -> MagicMock:
    service = MagicMock(spec=MeterServiceZwave)
    service.refresh_meter_zwave = refresh
    device = MagicMock(spec=QolsysAutomationDeviceZwave)
    device._FIX_MULTICHANNEL_METER_ENDPOINT = True
    device.prefix = name
    device.service_get_protocol.return_value = [service]
    return device


def make_controller(devices: list[Any], monkeypatch: pytest.MonkeyPatch) -> QolsysController:
    controller = QolsysController()
    controller._controller_state = ControllerState.CONNECTED
    controller.state._automation_devices = devices

    async def fake_sleep(delay: float) -> None:
        if delay == 300:  # End of the first pass
            raise asyncio.CancelledError

    monkeypatch.setattr("qolsys_controller.controller.asyncio.sleep", fake_sleep)
    return controller


async def run_one_pass(controller: QolsysController) -> None:
    with pytest.raises(asyncio.CancelledError):
        await controller.mqtt_zwave_meter_update()


async def test_timeout_is_logged_without_traceback(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    failing = AsyncMock(side_effect=QolsysOperationTimeoutError())
    healthy = AsyncMock()
    controller = make_controller([make_device("a", failing), make_device("b", healthy)], monkeypatch)

    with caplog.at_level(logging.WARNING, logger="qolsys_controller.controller"):
        await run_one_pass(controller)

    healthy.assert_awaited_once()
    records = [r for r in caplog.records if "meter refresh" in r.message]
    assert [r.levelno for r in records] == [logging.WARNING]
    assert records[0].exc_info is None


async def test_unexpected_error_keeps_running_and_logs_traceback(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    failing = AsyncMock(side_effect=ValueError("bad meter scale"))
    healthy = AsyncMock()
    controller = make_controller([make_device("a", failing), make_device("b", healthy)], monkeypatch)

    with caplog.at_level(logging.WARNING, logger="qolsys_controller.controller"):
        await run_one_pass(controller)

    healthy.assert_awaited_once()
    records = [r for r in caplog.records if "meter refresh" in r.message]
    assert [r.levelno for r in records] == [logging.ERROR]
    assert records[0].exc_info is not None


async def test_removing_a_device_mid_pass_does_not_skip_others(monkeypatch: pytest.MonkeyPatch) -> None:
    devices: list[Any] = []

    async def remove_self() -> None:
        devices.pop(0)

    second = AsyncMock()
    third = AsyncMock()
    devices.extend([make_device("a", AsyncMock(side_effect=remove_self)), make_device("b", second), make_device("c", third)])
    controller = make_controller(devices, monkeypatch)

    await run_one_pass(controller)

    second.assert_awaited_once()
    third.assert_awaited_once()
