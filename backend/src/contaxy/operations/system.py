from abc import ABC, abstractmethod

from contaxy.schema.system import SystemInfo


class SystemOperations(ABC):
    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        pass
