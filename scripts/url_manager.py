from abc import ABC, abstractmethod

from path_manager import PathManager


class UrlMapper(ABC):
    @abstractmethod
    def for_device(self, device_name: str) -> str:
        pass
    @abstractmethod
    def for_module(self, module_name: str) -> str:
        pass
    @abstractmethod
    def for_oam(self, oam_name: str) -> str:
        pass

class PageUrlMapper(UrlMapper):
    def for_device(self, device_name: str) -> str:
        return f"/devices/{PathManager.to_device_pathname(device_name)}"
    def for_module(self, module_name: str) -> str:
        return f"/ofm/{module_name}"
    def for_oam(self, oam_name: str) -> str:
        return f"/oam/{oam_name}"

class WikiUrlMapper(UrlMapper):
    def for_device(self, device_name: str) -> str:
        return f"https://device.openknx.de/{PathManager.to_device_pathname(device_name)}"
    def for_module(self, module_name: str) -> str:
        return f"https://github.com/OpenKNX/{module_name}"
    def for_oam(self, oam_name: str) -> str:
        return f"https://github.com/OpenKNX/{oam_name}"
