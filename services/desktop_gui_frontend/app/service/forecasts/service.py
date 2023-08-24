from app.service.exceptions import BackendConnectionError
from app.service.forecasts.backend import ForecastsBackend


def get_title_employees_forecast_growth(
        title_name: str,
        years_count: int,
        backend: ForecastsBackend
) -> dict[int, int]:

    try:
        return backend.get_title_employees_forecast_growth(title_name, years_count)
    except BackendConnectionError:
        raise
