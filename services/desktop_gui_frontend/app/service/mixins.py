from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    @abstractmethod
    def notify(self) -> None:
        raise NotImplementedError


class ObservableMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.observers: list[Observer] = []

    def attach_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def detach_observer(self, observer: Observer) -> None:
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in self.observers:
            observer.notify()
