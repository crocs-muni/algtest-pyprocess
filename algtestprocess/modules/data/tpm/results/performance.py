from typing import Optional

from overrides import overrides

from algtestprocess.modules.data.tpm.results.base import MeasurementResultTPM
from algtestprocess.modules.data.tpm.utils import null_if_none


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

    @overrides
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
