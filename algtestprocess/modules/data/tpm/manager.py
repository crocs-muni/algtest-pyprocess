import logging
import os.path
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
    SupportParserTPM, SupportParserTPMQuicktestYAML


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

        # First we try the easiest option, parsing the yaml file
        # present in the latest versions of tpm2-algtest
        file_path = os.path.join(self._root_path, 'performance.yaml')
        try:
            profile = PerformanceParserTPMYaml(file_path).parse()
        except yaml.YAMLError as err:
            logging.warning(
                f"Could not parse performance profile at {file_path=}"
                f", possibly caused by old version of the measurement."
                f"Will try other parser implementations.")

            profile = PerformanceParserTPM(file_path).parse()

            if profile is None or len(profile.results) == 0:
                logging.error(
                    f"Old parser implementation was not successful, for "
                    f"performance profile file at {file_path=}."
                )

        except FileNotFoundError as err:
            logging.warning(
                f"Performance profile file at {file_path=} was not found,"
                "older measurements have csv file in performance folder instead.")

            performance_path = os.path.join(self._root_path, 'performance')
            try:
                assert os.path.exists(performance_path) and os.path.isdir(
                    performance_path)
            except (FileNotFoundError, AssertionError):
                logging.error(
                    f"performance folder not found or is not a directory "
                    f"at {performance_path=}")
                return None

            files = [x.name for x in os.scandir(performance_path)]
            assert len(files) == 1

            file_path = os.path.join(performance_path, files[0])
            profile = PerformanceParserTPM(file_path).parse()

            if profile is None:
                logging.error(f"csv file could not be parsed at {file_path=}")

        self._perf_handle = profile
        return profile

    def _post_process_support_profile(self,
                                      profile: Optional[ProfileSupportTPM]):
        if profile is None:
            return

        detail_path = os.path.join(self._root_path, 'detail')
        try:
            assert os.path.exists(detail_path) and os.path.isdir(detail_path)
        except (FileNotFoundError, AssertionError):
            logging.error("detail folder not found or is not a directory "
                          f"at {detail_path=}")
            return

        quicktest_profile = \
            SupportParserTPMQuicktestYAML(detail_path, strict=False).parse()

        if quicktest_profile is None or len(quicktest_profile.results) == 0:
            logging.warning(f"quicktest parser failed at {detail_path=}")
            return

        # If the Quicktest Profile found out some missing entries, we add them
        for key, obj in quicktest_profile.results.items():
            if profile.results.get(key) is None:
                profile.results[key] = obj

    @property
    def support_profile(self) -> Optional[ProfileSupportTPM]:
        if self._supp_handle:
            return self._supp_handle

        # First we try the easiest option, that is yaml file
        # created by latest versions of tpm2-algtest

        file_path = os.path.join(self._root_path, 'results.yaml')
        try:
            profile = SupportParserTPMYaml(file_path).parse()
        except yaml.YAMLError as err:
            logging.warning(
                f"Could not parse support profile at {file_path=}"
                f", possibly caused by old version of the measurement."
                f"Will try other parser implementations.")

            profile = SupportParserTPM(file_path).parse()

            if profile is None or len(profile.results) == 0:
                logging.error(
                    "Old parser implementation was not successful"
                    f"for support profile file at {file_path=}")

        except FileNotFoundError as err:
            logging.warning(
                f"Support profile file at {file_path=} was not found,"
                "older measurements have csv file in results folder instead.")

            results_path = os.path.join(self._root_path, 'results')
            try:
                assert os.path.exists(results_path) and \
                       os.path.isdir(results_path)
            except (FileNotFoundError, AssertionError):
                logging.error(
                    f"results folder not found or is not a directory "
                    f"at {results_path=}")
                return None

            files = [x.name for x in os.scandir(results_path)]
            assert len(files) == 1

            file_path = os.path.join(results_path, files[0])
            profile = SupportParserTPM(file_path).parse()

            if profile is None or len(profile.results) == 0:
                logging.error(f"csv file could not be parsed at {file_path=}")

        # Lastly we run the Quicktest files parser so that we possibly
        # retrieve some missed measurements. If it does not succeed,
        # we ignore it.

        self._post_process_support_profile(profile)

        # Finally we need to make sure that the profile has name for TPM
        # if not we log it and fail.

        checks = [
            profile.manufacturer is None,
            profile.firmware_version is None,
            profile.device_name == ''
        ]
        if any(checks):
            logging.error(f"could not retrieve TPM identification "
                          f"(manufacturer, firmware version) at {file_path=}")
            return None

        self._supp_handle = profile
        return profile

    @property
    def cryptoprops(self) -> Optional[CryptoProps]:
        if self._cpps_handle:
            return self._cpps_handle

        path = f"{self._root_path}/detail"

        profile = CryptoPropsParser(path).parse()

        if not profile:
            return None

        # To get TPM device name ... we need to parse supp or perf profile
        handle = self.support_profile

        if handle is None:
            logging.error(
                f"TPMProfileManager: Unable to load support profile "
                f"for {self._root_path}"
            )

        if handle:
            profile.manufacturer = handle.manufacturer
            profile.vendor_string = handle.vendor_string
            profile.firmware_version = handle.firmware_version

        self._cpps_handle = profile
        return profile
