from typing import Dict

from overrides import overrides

from algtestprocess.modules.profiles.tpm.base import ProfileTPM
from algtestprocess.modules.data.tpm.results.support import SupportResultTPM


class ProfileSupportTPM(ProfileTPM):
    """TPM profile with support results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[str, SupportResultTPM] = {}

    @overrides
    def add_result(self, result):
        if result.name:
            self.results[result.name] = result

    @overrides
    def export(self):
        data = super(ProfileSupportTPM, self).export()
        data.update({
            "results_type": "support",
            "results": [result.export() for result in self.results.values()]
        })
        return data
