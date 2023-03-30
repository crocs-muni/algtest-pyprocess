from typing import Optional, List

import pandas as pd

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory


class CryptoPropResult:
    def __init__(self):
        self.category: Optional[CryptoPropResultCategory] = None
        self.path: Optional[str] = None
        self.delimiters: List[str] = [",", ";"]
        self._data: Optional[pd.DataFrame] = None
        self.merged: bool = False

    @property
    def data(self) -> pd.DataFrame:
        assert self.path or (self.merged and self._data)
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

    def __add__(self, other):
        assert isinstance(other, CryptoPropResult)
        new = CryptoPropResult()
        new.category = self.category
        new.merged = True
        new.path = f"{self.path}:{other.path}"

        my_data = self.data
        other_data = self.data

        if my_data is None and other_data is None:
            return new

        if my_data is None:
            new._data = other_data
            return new

        if other_data is None:
            new._data = my_data
            return new

        new._data = pd.concat([my_data, other_data])
        return new
