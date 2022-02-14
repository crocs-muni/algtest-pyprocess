from typing import List, Optional


class PerformanceResultTPM:
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


class ProfilePerformanceTPM:
    def __init__(self):
        self.test_info = {}
        self.results: List[PerformanceResultTPM] = []
