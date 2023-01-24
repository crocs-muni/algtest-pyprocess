from typing import Optional

from algtestprocess.modules.data.tpm.results.base import MeasurementResultTPM


class SupportResultTPM(MeasurementResultTPM):
    """Class to store support results for TPMs"""

    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None
        self.value: Optional[str] = None