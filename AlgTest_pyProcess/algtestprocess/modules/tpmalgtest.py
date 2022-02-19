from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from overrides import overrides


class PerformanceResultTPM:
    """Class to store performance results for TPMs"""

    def __init__(self):
        self.category: Optional[str] = None
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


class SupportResultTPM:
    """Class to store support results for TPMs"""

    def __init__(self):
        self.category: Optional[str] = None
        self.name: Optional[str] = None
        self.value: Optional[str] = None


class ProfileTPM(ABC):
    """TPM base profile class"""

    def __init__(self):
        self.test_info = {}

    @abstractmethod
    def add_result(self, result):
        pass


class ProfilePerformanceTPM(ProfileTPM):
    """TPM profile with performance results"""

    def __init__(self):
        super().__init__()
        self.results: List[PerformanceResultTPM] = []

    @overrides
    def add_result(self, result):
        self.results.append(result)


class ProfileSupportTPM(ProfileTPM):
    """TPM profile with support results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[str, SupportResultTPM] = {}

    @overrides
    def add_result(self, result):
        self.results[result.name] = result
