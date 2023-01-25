import os.path
from sys import stderr
from typing import Optional

import yaml

from algtestprocess.modules.data.tpm.profiles.cryptoprops import CryptoProps
from algtestprocess.modules.data.tpm.profiles.performance import \
    ProfilePerformanceTPM
from algtestprocess.modules.data.tpm.profiles.support import ProfileSupportTPM
from algtestprocess.modules.parser.tpm.cryptoprops import CryptoPropsParser
from algtestprocess.modules.parser.tpm.performance import \
    PerformanceParserTPMYaml
from algtestprocess.modules.parser.tpm.support import SupportParserTPMYaml


class TPMProfileManager:
    """
    This class is used for managing of the TPM profile objects

    Its responsibilities are:

    Lazy loading the data into profile objects
    - it stores the path to the root folder of measurements

    """

    def __init__(self, path: str):
        self._perf_handle: Optional[ProfilePerformanceTPM] = None
        self._supp_handle: Optional[ProfileSupportTPM] = None
        self._cpps_handle: Optional[CryptoProps] = None

        assert os.path.exists(path) and os.path.isdir(path)

        self._root_path: str = path

    @property
    def performance_profile(self) -> Optional[ProfilePerformanceTPM]:
        if self._perf_handle:
            return self._perf_handle

        # Easy, we know the filename.
        yaml_path = f"{self._root_path}/performance.yaml"

        try:
            profile = PerformanceParserTPMYaml(yaml_path).parse()
        except yaml.YAMLError:
            # TODO: logger
            print(f"TPMProfileManager: Couldn't parse perf profile",
                  file=stderr)
            return None

        # TODO: Based on image tag for older measurements infer the
        #       project structure. Necessary for measurements created
        #       by older versions of tpm2-algtest
        self._perf_handle = profile
        return profile

    @property
    def support_profile(self) -> Optional[ProfileSupportTPM]:
        if self._supp_handle:
            return self._supp_handle

        yaml_path = f"{self._root_path}/results.yaml"

        try:
            profile = SupportParserTPMYaml(yaml_path).parse()
        except yaml.YAMLError:
            print(f"TPMProfileManager: Couldn't parse supp profile",
                  file=stderr)
            return None

        # TODO: Same as previous
        self._supp_handle = profile
        return profile

    @property
    def cryptoprops(self) -> Optional[CryptoProps]:
        if self._cpps_handle:
            return self._cpps_handle

        path = f"{self._root_path}/detail"

        # TODO: 1. Infer delimiters based on image tag
        #       2. Somehow infer device name without parsing the supp or perf p.

        profile = CryptoPropsParser(path).parse()
        self._cpps_handle = profile
        return profile
