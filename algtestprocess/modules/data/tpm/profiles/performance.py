from typing import Dict

from overrides import overrides

from algtestprocess.modules.data.tpm.profiles.base import ProfileTPM
from algtestprocess.modules.data.tpm.results.performance import \
    PerformanceResultTPM


class ProfilePerformanceTPM(ProfileTPM):
    """TPM profile with performance results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[str, PerformanceResultTPM] = {}

    @overrides
    def add_result(self, result):
        # Result name representation required to be unique
        name = f"{result.category}" if result.category else ""
        name += f" {result.key_params}" if result.key_params else ""
        name += f" {result.algorithm}" if result.algorithm else ""
        name += f" {result.mode}" if result.mode else ""
        name += f" {result.encrypt_decrypt}" if result.encrypt_decrypt else ""
        name += f" {result.scheme}" if result.scheme else ""
        name = name.lstrip(' ')
        self.results[name] = result
        return name
