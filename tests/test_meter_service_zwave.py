"""Tests for MeterServiceZwave report decoding."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from qolsys_controller.automation_zwave.service_meter import MeterServiceZwave
from qolsys_controller.enum_qolsys import QolsysMeterRateType, QolsysMeterScale, QolsysMeterType

from .zwave_service_helpers import make_zwave_device


def _make(endpoint: int = 0) -> tuple[MeterServiceZwave, MagicMock]:
    device = make_zwave_device()
    return MeterServiceZwave(automation_device=device, endpoint=endpoint), device


def _data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "meter_type": "ENERGY_METER",
        "meter_ratetype_supported": 1,  # IMPORT
        "meter_master_reset_flag": True,
        "meter_scale_supported": '["KWH", "WATTS"]',
        "meter_scale_reading_values": {"KWH": "12.5", "WATTS": "340"},
    }
    data.update(overrides)
    return data


class TestMeterServiceZwave:
    def test_service_name(self) -> None:
        service, _ = _make()
        assert service.service_name == "MeterService"

    def test_decodes_type_rate_and_reset_flag(self) -> None:
        service, _ = _make()
        service.update_zwave_service(_data())
        assert service.meter_type == QolsysMeterType.ELECTRIC_METER
        assert service.rate_type == QolsysMeterRateType.IMPORT
        assert service.master_reset_flag is True

    def test_supported_scales_create_meters(self) -> None:
        service, _ = _make()
        service.update_zwave_service(_data())
        assert set(service.supported_scales) == {QolsysMeterScale.KWH, QolsysMeterScale.WATTS}
        assert service.meter(QolsysMeterScale.KWH) is not None
        assert service.meter(QolsysMeterScale.WATTS) is not None

    def test_reading_values_populate_meters(self) -> None:
        service, _ = _make()
        service.update_zwave_service(_data())
        assert service.meter(QolsysMeterScale.KWH).value == 12.5
        assert service.meter(QolsysMeterScale.WATTS).value == 340.0

    def test_invalid_rate_type_falls_back_to_unspecified(self) -> None:
        service, _ = _make()
        service.update_zwave_service(_data(meter_ratetype_supported=99))
        assert service.rate_type == QolsysMeterRateType.UNSPECIFIED

    def test_update_meter_value_false_skips_readings(self) -> None:
        service, _ = _make()
        service.update_zwave_service(_data(), update_meter_value=False)
        # Scales (and their meters) are still registered, but with no values yet.
        assert set(service.supported_scales) == {QolsysMeterScale.KWH, QolsysMeterScale.WATTS}
        assert service.meter(QolsysMeterScale.KWH).value is None
