from abc import ABC, abstractmethod
from typing import Sequence

from . import commands


class CommandEditor(ABC):
    @abstractmethod
    def edit_multicommand(self, cmd: "commands.MultiCommand") -> None:
        ...

    @abstractmethod
    def edit_add_employee(self, cmd: "commands.AddEmployee") -> None:
        ...

    @abstractmethod
    def edit_update_employee(self, cmd: "commands.UpdateEmployee") -> None:
        ...

    @abstractmethod
    def edit_delete_employees(self, cmd: "commands.DeleteEmployees") -> None:
        ...


class UpdateEmployeesIDs(CommandEditor):
    def __init__(self, old_ids: Sequence[int], new_ids: Sequence[int]) -> None:
        self.old_ids = old_ids
        self.new_ids = new_ids

    def edit_multicommand(self, cmd: "commands.MultiCommand") -> None:
        cmd.local_commands_history.update_employees_ids(self.old_ids, self.new_ids)

    def edit_add_employee(self, cmd: "commands.AddEmployee") -> None:
        id_index = self.old_ids.index(cmd.added_employee_id)
        if id_index == -1:
            return

        cmd.added_employee_id = self.new_ids[id_index]

    def edit_update_employee(self, cmd: "commands.UpdateEmployee") -> None:
        if not cmd.employee_before_update:
            return

        id_index = self.old_ids.index(cmd.employee_before_update.id)
        if id_index == -1:
            return

        cmd.employee_before_update.id = self.new_ids[id_index]

    def edit_delete_employees(self, cmd: "commands.DeleteEmployees") -> None:
        for emp in cmd.deleted_employees:
            emp_id_index = self.old_ids.index(emp.id)
            if emp_id_index == -1:
                return

            emp.id = self.new_ids[emp_id_index]
