"""Tests for AdcCommands.virtual_device_action func-id resolution and guards."""

from __future__ import annotations

import json
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from qolsys_controller.automation_adc.device import QolsysAutomationDeviceADC
from qolsys_controller.commands.adc import AdcCommands
from qolsys_controller.errors import InvalidVirtualNodeError, ServiceNotFoundError

# func_list with one controllable func (Heat Setpoint, vdFuncLocalControl 2) and
# two read-only funcs (Local Temperature and a setpoint limit, vdFuncLocalControl 1).
FUNC_LIST = (
    "["
    '{"vdFuncId":1,"vdFuncName":"Local Temperature","vdFuncLocalControl":1,"vdFuncType":4,"vdFuncState":720},'
    '{"vdFuncId":4,"vdFuncName":"Heat Setpoint","vdFuncLocalControl":2,"vdFuncType":21,"vdFuncState":680},'
    '{"vdFuncId":5,"vdFuncName":"Min Heat Setpoint Limit","vdFuncLocalControl":1,"vdFuncType":22,"vdFuncState":450}'
    "]"
)


def _make_commands(func_list: str = FUNC_LIST) -> tuple[AdcCommands, QolsysAutomationDeviceADC]:
    dev = QolsysAutomationDeviceADC(
        controller=MagicMock(),
        adc_dict={"_id": "2", "device_id": "99", "name": "Bedroom Thermostat", "func_list": func_list},
    )
    controller = MagicMock()
    controller.state.automation_device.return_value = dev
    return AdcCommands(controller), dev


def _sent_function(mock_panel: MagicMock) -> dict[str, Any]:
    """Decode the single virtualDeviceFunctionList entry the command sent."""
    ipc_request = mock_panel.return_value.append_ipc_request.call_args.args[0]
    virtual_command = json.loads(ipc_request[0]["dataValue"])
    device_list = json.loads(virtual_command["virtual_device_description"])
    return cast(dict[str, Any], device_list["virtualDeviceList"][0]["virtualDeviceFunctionList"][0])


class TestVirtualDeviceAction:
    async def test_controllable_func_sends_command(self) -> None:
        # Heat Setpoint (id 4, FULL_CONTROL) passes the guards and the outgoing
        # payload carries that id, its real vdFuncType (21), and the state.
        cmds, _ = _make_commands()
        with patch("qolsys_controller.commands.adc.MQTTCommand_Panel") as mock_panel:
            mock_panel.return_value.send_command = AsyncMock(return_value={"ok": True})
            result = await cmds.virtual_device_action("99", 4, 680)

        assert result == {"ok": True}
        func = _sent_function(mock_panel)
        assert func["vdFuncId"] == 4
        assert func["vdFuncType"] == 21
        assert func["vdFuncState"] == 680

    async def test_read_only_func_rejected(self) -> None:
        # Local Temperature (id 1, STATUS_ONLY) is not controllable.
        cmds, _ = _make_commands()
        with patch("qolsys_controller.commands.adc.MQTTCommand_Panel") as mock_panel:
            with pytest.raises(ServiceNotFoundError):
                await cmds.virtual_device_action("99", 1, 0)
            mock_panel.assert_not_called()

    async def test_read_only_setpoint_limit_rejected(self) -> None:
        # Min Heat Setpoint Limit (id 5, STATUS_ONLY) is not controllable.
        cmds, _ = _make_commands()
        with patch("qolsys_controller.commands.adc.MQTTCommand_Panel") as mock_panel:
            with pytest.raises(ServiceNotFoundError):
                await cmds.virtual_device_action("99", 5, 0)
            mock_panel.assert_not_called()

    async def test_unknown_func_id_rejected(self) -> None:
        cmds, _ = _make_commands()
        with patch("qolsys_controller.commands.adc.MQTTCommand_Panel") as mock_panel:
            with pytest.raises(ServiceNotFoundError):
                await cmds.virtual_device_action("99", 999, 0)
            mock_panel.assert_not_called()

    async def test_non_adc_device_raises_invalid_node(self) -> None:
        controller = MagicMock()
        controller.state.automation_device.return_value = MagicMock()  # not a QolsysAutomationDeviceADC
        cmds = AdcCommands(controller)
        with pytest.raises(InvalidVirtualNodeError):
            await cmds.virtual_device_action("99", 4, 680)
