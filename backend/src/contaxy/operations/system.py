from abc import ABC, abstractmethod

from contaxy.schema.system import SystemInfo, SystemStatistics


class SystemOperations(ABC):
    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        pass

    @abstractmethod
    def get_system_statistics(self) -> SystemStatistics:
        pass

    @abstractmethod
    def initialize_system(self) -> None:
        pass
