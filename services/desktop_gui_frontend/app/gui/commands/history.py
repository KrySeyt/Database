from typing import Any, Sequence

from . import commands
from . import editors


class CommandsHistory:
    def __init__(self) -> None:
        self.commands: "list[commands.Command]" = []

    def revert_prev_command(self) -> None:
        if self.commands:
            self.commands.pop().reverse()

    def revert_all(self) -> None:
        while self.commands:
            self.commands.pop().reverse()

    def add_command(self, command: "commands.Command") -> None:
        self.commands.append(command)

    def copy(self) -> "CommandsHistory":
        history = CommandsHistory()
        history.commands = [cmd.copy() for cmd in self.commands]
        return history

    def remove(self, command: "commands.Command") -> None:
        self.commands.remove(command)

    def clear(self) -> None:
        self.commands.clear()

    def employees_ids_changed(self, old_ids: Sequence[int], new_ids: Sequence[int]) -> None:
        self.update_employees_ids(old_ids, new_ids)

    def __len__(self) -> int:
        return len(self.commands)

    def update_employees_ids(self, old_ids: Sequence[int], new_ids: Sequence[int]) -> None:
        updater = editors.UpdateEmployeesIDs(old_ids, new_ids)
        for cmd in self.commands:
            cmd.accept_editing(updater)


class MultiCommandHistory(CommandsHistory):
    def __init__(self, parent_history: CommandsHistory, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.parent_history = parent_history

    def employees_ids_changed(self, old_ids: Sequence[int], new_ids: Sequence[int]) -> None:
        self.parent_history.employees_ids_changed(old_ids, new_ids)

    def copy(self) -> "MultiCommandHistory":
        history_copy = MultiCommandHistory(self.parent_history)
        history_copy.commands = [cmd.copy() for cmd in self.commands]
        return history_copy
