"""Tests for CoverServiceZwave command dispatch and capability checks."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.automation_zwave.service_cover import CoverServiceZwave
from qolsys_controller.enum_zwave import ZwaveCommandClass

from .zwave_service_helpers import make_zwave_device


def _make(
    *,
    supports_barrier: bool = True,
    spec: bool = False,
    endpoint: int = 0,
) -> tuple[CoverServiceZwave, MagicMock]:
    command_classes = [ZwaveCommandClass.BarrierOperator] if supports_barrier else []
    device = make_zwave_device(command_classes=command_classes, spec=spec)
    return CoverServiceZwave(automation_device=device, endpoint=endpoint), device


class TestCoverServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "CoverService"

    @pytest.mark.asyncio
    async def test_open_sends_barrier_operator_full(self) -> None:
        # The transitional is_opening flag is pulsed via notify then reset to
        # False inside open(), so only the dispatched command is asserted here.
        service, device = _make(endpoint=3)
        await service.open()
        device.controller.commands.zwave.barrier_operator_set.assert_awaited_once_with("6", "3", 0xFF)

    @pytest.mark.asyncio
    async def test_close_sends_barrier_operator_zero(self) -> None:
        service, device = _make(endpoint=3)
        await service.close()
        device.controller.commands.zwave.barrier_operator_set.assert_awaited_once_with("6", "3", 0x00)

    def test_supports_open_close_true_with_barrier(self) -> None:
        # isinstance(device, QolsysAutomationDeviceZwave) must pass -> spec=True
        service, _ = _make(supports_barrier=True, spec=True)
        assert service.supports_open() is True
        assert service.supports_close() is True

    def test_supports_open_close_false_without_barrier(self) -> None:
        service, _ = _make(supports_barrier=False, spec=True)
        assert service.supports_open() is False
        assert service.supports_close() is False

    def test_supports_open_false_for_non_zwave_device(self) -> None:
        # Plain mock fails the isinstance guard -> capability reported as False.
        service, _ = _make(supports_barrier=True, spec=False)
        assert service.supports_open() is False

    def test_supports_stop_and_position_false(self) -> None:
        service, _ = _make()
        assert service.supports_stop() is False
        assert service.supports_position() is False
