from abc import ABC, abstractmethod
from typing import Optional

from overrides import EnforceOverrides


class ProfileTPM(ABC, EnforceOverrides):
    """TPM base profile class"""

    def __init__(self):
        self.test_info = {}

    def device_name(self) -> Optional[str]:
        if not self.test_info.get('TPM name'):
            manufacturer = self.test_info.get('Manufacturer')
            version = self.test_info.get('Firmware version')
            self.test_info['TPM name'] = f"{manufacturer} {version}"
        return self.test_info.get('TPM name')

    def rename(self, name: str):
        self.test_info['TPM name'] = name

    @abstractmethod
    def add_result(self, result):
        pass

    def export(self):
        return {"test_info": self.test_info}
