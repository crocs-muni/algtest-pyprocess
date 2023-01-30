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
    PerformanceParserTPMYaml, PerformanceParserTPM
from algtestprocess.modules.parser.tpm.support import SupportParserTPMYaml, \
    SupportParserTPM


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
        try:
            file_path = os.path.join(self._root_path, 'performance.yaml')
            profile = PerformanceParserTPMYaml(file_path).parse()
        except yaml.YAMLError as err:
            # TODO: logger, this is ugly
            print(f"TPMProfileManager: Couldn't parse perf profile"
                  f"\n{err}"
                  f"\nTrying old parser implementation",
                  file=stderr)

            profile = PerformanceParserTPM(file_path).parse()

            print(f"Old parser implementation was ", end="", file=stderr)
            if not profile.results:
                print("not ", end="", file=stderr)
                profile = None
            print("successful.")

        except FileNotFoundError as err:
            print("Older version of tpm2-algtest did not use yaml format.\n"
                  "Trying performance folder for csv file",
                  file=stderr)
            performance_path = os.path.join(self._root_path, 'performance')
            assert os.path.exists(performance_path) and os.path.isdir(
                performance_path)

            files = [x.name for x in os.scandir(performance_path)]
            assert len(files) == 1

            profile = PerformanceParserTPM(
                os.path.join(performance_path, files[0])).parse()

        # TODO: Based on image tag for older measurements infer the
        #       project structure. Necessary for measurements created
        #       by older versions of tpm2-algtest
        self._perf_handle = profile
        return profile

    @property
    def support_profile(self) -> Optional[ProfileSupportTPM]:
        if self._supp_handle:
            return self._supp_handle

        try:
            file_path = os.path.join(self._root_path, 'results.yaml')
            profile = SupportParserTPMYaml(file_path).parse()
        except yaml.YAMLError as err:
            print(f"TPMProfileManager: Couldn't parse supp profile"
                  f"\n{err}"
                  f"\nTrying old parser implementation",
                  file=stderr)
            profile = SupportParserTPM(file_path).parse()

            print(f"Old parser implementation was ", end="", file=stderr)
            if not profile.results:
                print("not ", end="", file=stderr)
                profile = None
            print("successful.")

        except FileNotFoundError as err:
            print("Older version of tpm2-algtest did not use yaml format.\n"
                  "Trying results folder for csv file",
                  file=stderr)
            results_path = os.path.join(self._root_path, 'results')
            assert os.path.exists(results_path) and os.path.isdir(results_path)

            files = [x.name for x in os.scandir(results_path)]
            assert len(files) == 1

            file_path = os.path.join(results_path, files[0])
            profile = SupportParserTPM(file_path).parse()

        # TODO: Same as previous
        self._supp_handle = profile
        return profile

    @property
    def cryptoprops(self) -> Optional[CryptoProps]:
        if self._cpps_handle:
            return self._cpps_handle

        path = f"{self._root_path}/detail"

        # TODO: 1. Infer delimiters based on image tag
        # TODO: 2. Somehow infer device name without parsing the supp or perf p.

        profile = CryptoPropsParser(path).parse()

        if not profile:
            return None

        # To get TPM device name ... we need to parse supp or perf profile
        handle = self.support_profile

        if handle is None:
            print(
                f"TPMProfileManager: Unable to load support profile "
                f"for {self._root_path}"
            )

        if handle:
            profile.manufacturer = handle.manufacturer
            profile.vendor_string = handle.vendor_string
            profile.firmware_version = handle.firmware_version

        self._cpps_handle = profile
        return profile
