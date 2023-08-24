import requests

from ..exceptions import BackendConnectionError, BackendServerError


class ForecastsBackend:
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def get_title_employees_forecast_growth(self, title_name: str, years_count: int) -> dict[int, int]:
        endpoint_url = rf"{self.backend_url}/forecasts/title_employees_growth/{years_count}"

        try:
            response = requests.post(
                endpoint_url,
                json={"name": title_name}
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        if response.ok:
            return {int(k): v for k, v in response.json().items()}
        else:
            return {}
