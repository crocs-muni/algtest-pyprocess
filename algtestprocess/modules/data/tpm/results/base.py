from typing import Optional

from overrides import EnforceOverrides


class MeasurementResultTPM(EnforceOverrides):
    def __init__(self):
        self.category: Optional[str] = None
