from typing import Optional

from overrides import overrides

from algtestprocess.modules.data.tpm.results.base import MeasurementResultTPM
from algtestprocess.modules.data.tpm.utils import null_if_none


class SupportResultTPM(MeasurementResultTPM):
    """Class to store support results for TPMs"""

    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None
        self.value: Optional[str] = None

    @overrides
    def export(self):
        data = super(SupportResultTPM, self).export()
        data.update({
            "name": null_if_none(self.name),
            "value": null_if_none(self.value)
        })
        return data
