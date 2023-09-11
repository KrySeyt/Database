import http
from typing import Any

import requests

from . import schema
from .service import StorageImp
from .exceptions import WrongEmployeeData
from ..exceptions import BackendConnectionError, BackendServerError


class StorageBackend(StorageImp):
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

                errors_places: list[tuple[Any, ...]] = []
                messages: list[str] = []
                errors_types: list[str] = []
                for err_info in response.json()["detail"]:
                    errors_places.append(tuple(err_info["loc"][1:]))
                    messages.append(err_info["msg"])
                    errors_types.append(err_info["type"])

                raise WrongEmployeeData(errors_places, messages, errors_types)

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

            errors_places: list[tuple[Any, ...]] = []
            messages: list[str] = []
            errors_types: list[str] = []
            for err_info in response.json()["detail"]:
                errors_places.append(tuple(err_info["loc"][1:]))
                messages.append(err_info["msg"])
                errors_types.append(err_info["type"])

            raise WrongEmployeeData(errors_places, messages, errors_types)

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
