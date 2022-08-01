from abc import ABC, abstractmethod
from typing import Optional, Dict

from overrides import overrides

def null_if_none(x: any):
    return 'null' if x is None else x

def bool_to_tf(x: bool) -> str:
    return 'true'if x else 'false'

class MeasurementResultTPM:
    def __init__(self):
        self.category: Optional[str] = None

    def export(self):
        return {"category": null_if_none(self.category)}


class PerformanceResultTPM(MeasurementResultTPM):
    """Class to store performance results for TPMs"""

    def __init__(self):
        super().__init__()
        self.key_params: Optional[str] = None

        self.algorithm: Optional[str] = None
        self.key_length: Optional[int] = None
        self.mode: Optional[str] = None
        self.encrypt_decrypt: Optional[str] = None
        self.data_length: Optional[int] = None
        self.scheme: Optional[str] = None

        self.operation_avg: Optional[float] = None
        self.operation_min: Optional[float] = None
        self.operation_max: Optional[float] = None

        self.iterations: Optional[int] = None
        self.successful: Optional[int] = None
        self.failed: Optional[int] = None
        self.error: Optional[str] = None

    def export(self):
        data = super(PerformanceResultTPM, self).export()
        data.update({
            "key_params": null_if_none(self.key_params),
            "algorithm": null_if_none(self.algorithm),
            "key_length": null_if_none(self.key_length),
            "mode": null_if_none(self.mode),
            "encrypt_decrypt": null_if_none(self.encrypt_decrypt),
            "data_length": null_if_none(self.data_length),
            "scheme": null_if_none(self.scheme),
            "operation_avg": null_if_none(self.operation_avg),
            "operation_min": null_if_none(self.operation_min),
            "operation_max": null_if_none(self.operation_max),
            "iterations": null_if_none(self.iterations),
            "successful": null_if_none(self.successful),
            "failed": null_if_none(self.failed),
            "error": null_if_none(self.error)
        })
        return data


class SupportResultTPM(MeasurementResultTPM):
    """Class to store support results for TPMs"""

    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None
        self.value: Optional[str] = None

    def export(self):
        data = super(SupportResultTPM, self).export()
        data.update({
            "name": null_if_none(self.name),
            "value": null_if_none(self.value)
        })
        return data


class ProfileTPM(ABC):
    """TPM base profile class"""

    def __init__(self):
        self.test_info = {}

    def device_name(self) -> Optional[str]:
        return self.test_info.get('TPM name')

    def rename(self, name: str):
        self.test_info['TPM name'] = name

    @abstractmethod
    def add_result(self, result):
        pass

    def export(self):
        return {"test_info":self.test_info}


class ProfilePerformanceTPM(ProfileTPM):
    """TPM profile with performance results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[str, PerformanceResultTPM] = {}

    @overrides
    def add_result(self, result):
        # Result name representation required to be unique
        name = f"{result.category}"
        name += f" {result.key_params}" if result.key_params else ""
        name += f" {result.algorithm}" if result.algorithm else ""
        name += f" {result.mode}" if result.mode else ""
        name += f" {result.encrypt_decrypt}" if result.encrypt_decrypt else ""
        name += f" {result.scheme}" if result.scheme else ""
        self.results[name] = result
        return name

    def export(self):
        data = super(ProfilePerformanceTPM, self).export()
        data.update({
            "results_type": "performance",
            "results": [result.export() for result in self.results.values()]
        })
        return data



class ProfileSupportTPM(ProfileTPM):
    """TPM profile with support results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[str, SupportResultTPM] = {}

    @overrides
    def add_result(self, result):
        if result.name:
            self.results[result.name] = result

    def export(self):
        data = super(ProfileSupportTPM, self).export()
        data.update({
            "results_type": "support",
            "results": [result.export() for result in self.results.values()]
        })
        return data
