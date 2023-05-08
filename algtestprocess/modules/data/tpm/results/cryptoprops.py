import gc
import logging
from typing import Optional, List, Union

import pandas as pd

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory


class CryptoPropResult:
    def __init__(self):
        self.category: Optional[CryptoPropResultCategory] = None
        self.delimiters: List[str] = [",", ";"]
        self.merged: bool = False
        self._data = None
        self.paths: List[str] = []

    @property
    def data(self) -> Union[pd.DataFrame, str]:
        if self._data:
            return self._data

        df = None
        for path in self.paths:
            next_df = None
            for delim in self.delimiters:
                next_df = pd.read_csv(
                    path,
                    header=0,
                    delimiter=delim
                )
                if len(next_df.columns) > 1:
                    break

            if next_df is None:
                logging.warning(
                    f"CryptoPropResult.data:{path} could not be parsed")
                continue

            if df is None:
                df = next_df
            else:
                df = pd.concat([df, next_df])

        return df

    @data.setter
    def data(self, value):
        assert isinstance(value, str) or isinstance(value,
                                                    pd.DataFrame) or isinstance(
            value, list)
        self._data = value

    def __add__(self, other):
        assert isinstance(other, CryptoPropResult)
        new = CryptoPropResult()
        new.category = self.category
        new.merged = True
        new.paths = list(set(self.paths) | set(other.paths))
        if isinstance(self.data, str) and isinstance(other.data, str):
            new.data = [self.data, other.data]
        elif isinstance(self.data, list) or isinstance(other.data, list):
            new_data = []
            if isinstance(self.data, list):
                new_data += self.data
            elif not isinstance(self.data, pd.DataFrame):
                new_data += [self.data]

            if isinstance(other.data, list):
                new_data += other.data
            elif not isinstance(other.data, pd.DataFrame):
                new_data += [other.data]
            new.data = new_data
        gc.collect()
        return new
