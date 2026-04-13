"""Tests for QolsysPartition — alarm type mapping and updates."""

from __future__ import annotations

from qolsys_controller.enum_qolsys import PartitionAlarmState, PartitionAlarmType, PartitionSystemStatus
from qolsys_controller.partition import QolsysPartition


def _make_partition(**overrides: object) -> QolsysPartition:
    partition_dict = {"partition_id": "0", "name": "Home", "devices": ""}
    settings_dict = {
        "SYSTEM_STATUS": "DISARM",
        "SYSTEM_STATUS_CHANGED_TIME": "",
        "EXIT_SOUNDS": "ON",
        "ENTRY_DELAYS": "ON",
    }
    partition_dict.update(overrides.get("partition", {}))
    settings_dict.update(overrides.get("settings", {}))
    return QolsysPartition(
        partition_dict,
        settings_dict,
        alarm_state=overrides.get("alarm_state", PartitionAlarmState.NONE),
        alarm_type_array=overrides.get("alarm_types", []),
    )


class TestAlarmTypeMapping:
    def test_glass_break_maps_to_police(self) -> None:
        partition = _make_partition()
        partition.append_alarm_type([PartitionAlarmType.GLASS_BREAK])
        assert PartitionAlarmType.POLICE_EMERGENCY in partition.alarm_type_array

    def test_smoke_heat_maps_to_fire(self) -> None:
        partition = _make_partition()
        partition.append_alarm_type([PartitionAlarmType.SMOKE_HEAT])
        assert PartitionAlarmType.FIRE_EMERGENCY in partition.alarm_type_array

    def test_duplicate_alarm_types_deduped(self) -> None:
        partition = _make_partition()
        partition.append_alarm_type([PartitionAlarmType.GLASS_BREAK, PartitionAlarmType.ENTRY_EXIT_NORMAL_DELAY])
        assert partition.alarm_type_array.count(PartitionAlarmType.POLICE_EMERGENCY) == 1


class TestPartitionUpdate:
    def test_update_system_status(self) -> None:
        partition = _make_partition()
        partition.update_settings({"SYSTEM_STATUS": "ARM-STAY"})
        assert partition.system_status == PartitionSystemStatus.ARM_STAY

    def test_update_wrong_partition_ignored(self) -> None:
        partition = _make_partition()
        partition.update_partition({"partition_id": "99", "name": "Hacked"})
        assert partition.name == "Home"
