from typing import Dict, List

from overrides import overrides

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.profiles.base import ProfileTPM
from algtestprocess.modules.data.tpm.results.cryptoprops import CryptoPropResult


class CryptoProps(ProfileTPM):

    def __init__(self):
        super().__init__()
        self.results: Dict[CryptoPropResultCategory, CryptoPropResult] = {}

    @overrides
    def add_result(self, result):
        assert result.category
        category = result.category
        if not self.results.get(category):
            self.results[category] = result

    def free(self, categories: List[CryptoPropResultCategory]):
        for category in categories:
            result = self.results.get(category)
            if result:
                del result.data
