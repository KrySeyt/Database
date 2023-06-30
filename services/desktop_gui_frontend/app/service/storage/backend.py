import requests

from . import schema


class BackendConnectionError(IOError):
    pass


class StorageBackend:
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def add_employee(self, employee: schema.EmployeeIn) -> schema.Employee:
        endpoint_url = rf"{self.backend_url}/employee"

        try:
            response = requests.post(
                url=endpoint_url,
                json={
                    **employee.dict(),
                    "test": "any-text",
                      },
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        return schema.Employee.parse_obj(response.json())

    def get_employees(self, skip: int, limit: int) -> list[schema.Employee]:
        endpoint_url = rf"{self.backend_url}/employees"

        params = {
            "skip": skip,
            "limit": limit
        }

        try:
            response = requests.get(url=endpoint_url, params=params)
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        return [schema.Employee.parse_obj(i) for i in response.json()]
