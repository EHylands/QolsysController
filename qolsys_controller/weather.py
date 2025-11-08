import logging

from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)


class QolsysForecast:
    def __init__(self, data: dict) -> None:
        self._high_temp = data.get("high_temp", "")
        self._low_temp = data.get("low_temp", "")
        self._day_of_week = data.get("day_of_week", "")
        self._condition = data.get("condition", "")
        self._icon = data.get("icon", "")
        self._precipitation = data.get("precipitation", "")
        self._current_weather_date = data.get("current_weather_date", "")

    @property
    def high_temp(self) -> float | None:
        try:
            return float(self._high_temp)
        except ValueError:
            return None

    @property
    def low_temp(self) -> float | None:
        try:
            return float(self._low_temp)
        except ValueError:
            return None

    @property
    def day_of_week(self) -> str:
        return self._day_of_week

    @property
    def condition(self) -> str:
        return self._condition

    @property
    def precipitation(self) -> int | None:
        try:
            return int(self._precipitation)
        except ValueError:
            return None

    @property
    def current_weather_date(self) -> str:
        return self._current_weather_date


class QolsysWeather(QolsysObservable):
    def __init__(self) -> None:
        super().__init__()
        self._forecasts: list[QolsysForecast] = []

    def current_weather(self) -> QolsysForecast | None:
        if self._forecasts:
            return self._forecasts[0]
        return None

    def update(self, data: list[QolsysForecast]) -> None:
        self._forecasts.clear()
        for forecast_data in data:
            self._forecasts.append(forecast_data)

        self.notify()

    @property
    def forecasts(self) -> list[QolsysForecast]:
        return self._forecasts

    def to_dict(self) -> dict:
        pass
