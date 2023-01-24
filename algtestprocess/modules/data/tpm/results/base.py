from typing import Optional

from overrides import EnforceOverrides

from algtestprocess.modules.data.tpm.utils import null_if_none


class MeasurementResultTPM(EnforceOverrides):
    def __init__(self):
        self.category: Optional[str] = None

    def export(self):
        return {"category": null_if_none(self.category)}
