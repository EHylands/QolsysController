"""Tests for LockServiceZwave command dispatch and state decoding."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qolsys_controller.automation_zwave.service_lock import LockServiceZwave

from .zwave_service_helpers import make_zwave_device


def _make(
    *,
    is_locked: bool = False,
    status: str = "unlocked",
    endpoint: int = 0,
) -> tuple[LockServiceZwave, MagicMock]:
    device = make_zwave_device(status=status)
    service = LockServiceZwave(automation_device=device, endpoint=endpoint)
    service._is_locked = is_locked
    return service, device


class TestLockServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "LockService"

    def test_capabilities(self) -> None:
        service, _ = _make()
        assert service.supports_lock() is True
        assert service.supports_open() is False
        assert service.supports_jam() is False

    @pytest.mark.asyncio
    async def test_lock_when_unlocked_sends_doorlock_set_true(self) -> None:
        # is_locking is pulsed via notify then reset to False inside lock(),
        # so only the dispatched command is asserted here.
        service, device = _make(is_locked=False, endpoint=5)
        await service.lock()
        device.controller.commands.zwave.doorlock_set.assert_awaited_once_with("6", "5", True)

    @pytest.mark.asyncio
    async def test_unlock_when_locked_sends_doorlock_set_false(self) -> None:
        service, device = _make(is_locked=True, endpoint=5)
        await service.unlock()
        device.controller.commands.zwave.doorlock_set.assert_awaited_once_with("6", "5", False)

    @pytest.mark.asyncio
    async def test_lock_when_already_locked_is_noop(self) -> None:
        service, device = _make(is_locked=True)
        await service.lock()
        device.controller.commands.zwave.doorlock_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_unlock_when_already_unlocked_is_noop(self) -> None:
        service, device = _make(is_locked=False)
        await service.unlock()
        device.controller.commands.zwave.doorlock_set.assert_not_awaited()

    def test_update_marks_locked_when_status_locked(self) -> None:
        service, _ = _make(is_locked=False, status="Locked")
        service.update_automation_service()
        assert service.is_locked is True

    def test_update_marks_unlocked_when_status_unlocked(self) -> None:
        service, _ = _make(is_locked=True, status="unlocked")
        service.update_automation_service()
        assert service.is_locked is False
