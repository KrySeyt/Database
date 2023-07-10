import http
from typing import Any

import requests

from . import schema


class BackendConnectionError(IOError):
    pass


class BackendServerError(IOError):
    pass


class WrongData(IOError):
    def __init__(self, errors: list[schema.BackendWrongDataInfo], *args: Any) -> None:
        super().__init__(*args)
        self.errors = errors


class StorageBackend:
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def add_employee(self, employee: schema.EmployeeIn) -> schema.Employee:
        endpoint_url = rf"{self.backend_url}/storage/employee"

        try:
            response = requests.post(
                url=endpoint_url,
                data=employee.json(),
            )

        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        if response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY:
            assert "detail" in response.json().keys(), "No key \"Detail\" in error logs"

            errors_info = []
            for err_info in response.json()["detail"]:
                print(err_info)
                errors_info.append(schema.BackendWrongDataInfo(**err_info))

            raise WrongData(errors_info)

        return schema.Employee.parse_obj(response.json())

    def get_employees(self, skip: int, limit: int) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/storage/employees"

        params = {
            "skip": skip,
            "limit": limit
        }

        try:
            response = requests.get(url=endpoint_url, params=params)
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        employees = [schema.Employee.parse_obj(i) for i in response.json()]
        return employees

    def update_employee(self, employee: schema.EmployeeIn, employee_id: int) -> schema.Employee:
        endpoint_url = rf"{self.backend_url}/storage/employee/{employee_id}"

        try:
            response = requests.put(
                url=endpoint_url,
                json=employee.dict(),
            )

        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        if response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY:
            assert "detail" in response.json().keys(), "No key \"Detail\" in error logs"

            errors_info = []
            for err_info in response.json()["detail"]:
                errors_info.append(err_info)

            raise WrongData(errors_info)

        return schema.Employee.parse_obj(response.json())

    def delete_employees(self, employees_ids: list[int]) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/storage/employee"

        try:
            employees = []
            for id_ in employees_ids:
                response = requests.delete(url=rf"{endpoint_url}/{id_}",)

                if response.status_code >= 500:
                    raise BackendServerError

                if __debug__:
                    print(f"Status code: {response.status_code}")
                    print(response.json())

                employee = schema.Employee.parse_obj(response.json())
                employees.append(employee)

            return employees

        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

    def search_employees(self, employee_search_model: schema.EmployeeSearchModel) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/search/employees"

        try:
            response = requests.post(
                endpoint_url,
                json=employee_search_model.dict()
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        if response.status_code >= 500:
            raise BackendServerError

        if __debug__:
            print(f"Status code: {response.status_code}")
            print(response.json())

        return [schema.Employee.parse_obj(i) for i in response.json()]

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
