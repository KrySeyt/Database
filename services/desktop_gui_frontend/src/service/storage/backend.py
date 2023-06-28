import requests

from . import schema


class BackendConnectionError(IOError):
    pass


class StorageBackend:
    def __init__(self, backend_url: str) -> None:
        self.backend_url = backend_url

    def add_employee(self, employee: schema.EmployeeIn) -> schema.Employee:
        endpoint_url = f"{self.backend_url}/employee"

        try:
            response = requests.post(
                url=endpoint_url,
                json=employee.dict(),
            )
        except requests.exceptions.ConnectionError as err:
            raise BackendConnectionError from err

        return schema.Employee.parse_obj(response.json())
