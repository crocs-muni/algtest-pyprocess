from typing import Optional, List

import pandas as pd

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory


class CryptoPropResult:
    def __init__(self):
        self.category: Optional[CryptoPropResultCategory] = None
        self.path: Optional[str] = None
        self.delimiters: List[str] = [",", ";"]
        self._data: Optional[pd.DataFrame] = None

    @property
    def data(self) -> pd.DataFrame:
        assert self.path
        if self._data is None:
            for delim in self.delimiters:
                self._data = pd.read_csv(
                    self.path,
                    header=0,
                    delimiter=delim
                )
                if len(self._data.columns) > 1:
                    break
        return self._data

    @data.deleter
    def data(self):
        del self._data
