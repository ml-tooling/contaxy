from abc import ABC, abstractmethod
from typing import List

from contaxy.schema.system import AllowedImageInfo, SystemInfo, SystemStatistics


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

    @abstractmethod
    def list_allowed_images(self) -> List[AllowedImageInfo]:
        pass

    @abstractmethod
    def add_allowed_image(self, allowed_image: AllowedImageInfo) -> AllowedImageInfo:
        pass

    @abstractmethod
    def delete_allowed_image(self, allowed_image_name: str) -> None:
        pass

    @abstractmethod
    def check_allowed_image(self, image_name: str, image_tag: str) -> None:
        pass
