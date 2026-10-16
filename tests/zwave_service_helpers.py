"""Shared test helpers for Z-Wave automation service unit tests.

The Z-Wave ``service_*`` classes only touch a thin slice of their owning
``QolsysAutomationDeviceZwave``, so a configured ``MagicMock`` is enough to
unit-test command dispatch and state decoding without a live panel:

* ``virtual_node_id`` / ``command_class_list`` - read when dispatching commands
* ``status`` / ``extras`` - read by ``update_automation_service`` state refreshes
* ``to_dict_event()`` / ``notify()`` - fired by the service state setters
* ``controller.commands.zwave.*`` - awaited command dispatch (all ``AsyncMock``)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from qolsys_controller.enum_zwave import ZwaveCommandClass

# Every async command on ZWaveCommands, pre-wired as AsyncMock so that
# ``await device.controller.commands.zwave.<cmd>(...)`` works and can be asserted.
_ZWAVE_COMMANDS = (
    "barrier_operator_get",
    "barrier_operator_set",
    "central_scene_supported_get",
    "doorlock_get",
    "doorlock_set",
    "multi_channel_capability_get",
    "multi_channel_endpoint_get",
    "switch_binary_get",
    "switch_binary_set",
    "switch_multilevel_get",
    "switch_multilevel_set",
    "thermostat_fan_mode_get",
    "thermostat_fan_mode_set",
    "thermostat_fan_mode_supported_get",
    "thermostat_mode_get",
    "thermostat_mode_set",
    "thermostat_mode_supported_get",
    "thermostat_operating_state_get",
    "thermostat_setpoint_get",
    "thermostat_setpoint_set",
)


def make_zwave_device(
    *,
    virtual_node_id: str = "6",
    device_name: str = "Z-Wave Device",
    status: str = "on",
    extras: str = "{}",
    command_classes: list[ZwaveCommandClass] | None = None,
    spec: bool = False,
) -> MagicMock:
    """Return a MagicMock standing in for a QolsysAutomationDeviceZwave.

    Pass ``command_classes`` with the real ``ZwaveCommandClass`` members the
    device advertises - services gate dispatch on ``X in command_class_list``,
    and a bare MagicMock's ``__contains__`` always returns False, which would
    silently make every ``supports_*`` check fail.

    Set ``spec=True`` when the code under test does
    ``isinstance(automation_device, QolsysAutomationDeviceZwave)`` (e.g.
    ``LightServiceZwave.supports_level`` / ``CoverServiceZwave.supports_open``);
    a spec'd mock passes that check while a plain one does not.
    """
    if spec:
        # Imported lazily so the common (non-spec) path stays import-light.
        from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave

        device = MagicMock(spec=QolsysAutomationDeviceZwave)
    else:
        device = MagicMock()
    device.virtual_node_id = virtual_node_id
    device.device_name = device_name
    device.protocol.name = "ZWAVE"
    device.status = status
    device.extras = extras
    device.command_class_list = command_classes if command_classes is not None else []
    device.to_dict_event.return_value = {}

    zwave = device.controller.commands.zwave
    for command in _ZWAVE_COMMANDS:
        setattr(zwave, command, AsyncMock())

    return device
