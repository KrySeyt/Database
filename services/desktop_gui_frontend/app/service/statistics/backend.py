import http

import requests

from ..storage import schema
from ..exceptions import BackendConnectionError, BackendServerError
from .service import StatisticsImp


class StatisticsBackend(StatisticsImp):
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def get_max_work_duration_employees(self, employees_count: str) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/statistics/work_longest_employees/{employees_count}"

        try:
            response = requests.get(
                endpoint_url
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code == http.HTTPStatus.NOT_FOUND:
            return []

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        return [schema.Employee.parse_obj(i) for i in response.json()]

    def get_highest_paid_employees(self, employees_count: str) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/statistics/highest_paid_employees/{employees_count}"

        try:
            response = requests.get(
                endpoint_url
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code == http.HTTPStatus.NOT_FOUND:
            return []

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        return [schema.Employee.parse_obj(i) for i in response.json()]

    def get_title_employees_history_growth(self, title_name: str) -> dict[int, int]:
        endpoint_url = rf"{self.backend_url}/statistics/title_employees_growth_history"

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
