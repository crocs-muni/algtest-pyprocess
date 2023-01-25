from abc import ABC, abstractmethod

from overrides import EnforceOverrides


class ProfileTPM(ABC, EnforceOverrides):
    """TPM base profile class"""

    def __init__(self):
        self.test_info = {}

    @property
    def device_name(self):
        if not self.test_info.get('TPM name'):
            # Only way to reconstruct TPM name if it was not provided
            manufacturer = self.test_info.get('Manufacturer')
            version = self.test_info.get('Firmware version')
            self.test_info['TPM name'] = f"{manufacturer} {version}"
        return self.test_info.get('TPM name')

    @device_name.setter
    def device_name(self, value: str):
        self.test_info['TPM name'] = value

    @abstractmethod
    def add_result(self, result):
        pass
