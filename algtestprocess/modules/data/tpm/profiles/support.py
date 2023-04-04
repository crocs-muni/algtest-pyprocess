from typing import Dict

from overrides import overrides

from algtestprocess.modules.data.tpm.profiles.base import ProfileTPM
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

    def __str__(self):
        return str([x for x in self.results.keys()])
