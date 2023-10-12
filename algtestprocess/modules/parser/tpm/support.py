import os
import re
from typing import List, Callable, Any, Optional

from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.data.tpm.profiles.support import ProfileSupportTPM
from algtestprocess.modules.data.tpm.results.support import SupportResultTPM
from algtestprocess.modules.parser.tpm.utils import get_params


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(filter(None, map(lambda x: x.strip(), data))), \
        f.name.rsplit("/", 1)[1]


def get_data_yaml(path: str):
    data = None
    with open(path) as f:
        data = load(f, Loader)
    assert data
    return data


class SupportParserTPM:
    """
    TPM support profile parser
    Note: reads CSV support profiles for TPMs
    """

    def __init__(self, path: str):
        self.lines, self.filename = get_data(path)

    def parse_props_fixed(self, lines: List[str], result: SupportResultTPM):
        """Parse fixed properties section"""
        joined = "\n".join(lines)

        if "raw" not in joined and lines and "value" not in joined and lines:
            match = re.search("(?P<name>TPM[2]?_PT.+);[ ]*(?P<value>[^\n]+)",
                              lines[0])
            if not match:
                return 1
            result.name = match.group("name")
            result.value = match.group("value")

        else:
            items = [
                ("name", "(?P<name>TPM[2]?_PT.+)[;:]"),
                ("raw", "raw[:;][ ]*(?P<raw>0[x]?[0-9a-fA-F]*)"),
                ("value", 'value[:;][ ]*(?P<value>"?.*"?)'),
            ]
            params = get_params(joined, items)
            result.name = params.get("name")
            result.value = (
                params.get("value") if params.get("value") else params.get(
                    "raw")
            )
            shift = 0
            # Each result can have up to 1 to 3 rows
            for key, _ in items:
                shift += 1 if params.get(key) else 0

            return shift
        return 1

    def parse(self):
        try:
            profile = self._parse(legacy=False)
        except:
            try:
                profile = self._parse(legacy=True)
            except:
                return None
        if not profile.results:
            return None
        return profile

    def _parse(self, legacy: bool = False):
        profile = ProfileSupportTPM()
        lines = self.lines
        category = None
        i = 0
        while i < len(self.lines):
            current = lines[i]
            if "Quicktest" in current or "Capability" in current:
                category = current

            elif not category:
                split = current.split(":", maxsplit=1)
                if legacy:
                    split = current.split(";", maxsplit=1)
                key, val = split
                val = val.strip()
                profile.test_info[key] = val

            else:
                result = SupportResultTPM()
                val = None
                name = None
                current = current.replace(" ", "")

                if "properties-fixed" in category:
                    result.category = category
                    i += self.parse_props_fixed(lines[i: i + 3], result)
                    result.name = (
                        result.name.replace("TPM_",
                                            "TPM2_") if result.name else None
                    )
                    profile.add_result(result)
                    continue

                elif "algorithms" in category:
                    name = TPM2Identifier.ALG_ID_STR.get(int(current, 16))

                elif "commands" in category:
                    name = TPM2Identifier.CC_STR.get(int(current, 16))

                elif "ecc-curves" in category:
                    try:
                        if not re.match("0x[0-9a-f]+", current):
                            current = current.split(":")[1]
                        name = TPM2Identifier.ECC_CURVE_STR.get(
                            int(current, 16))
                    except ValueError:
                        i += 1
                        continue

                result.category = category
                result.name = name
                result.value = val
                if result.name:
                    profile.add_result(result)
            i += 1
        return profile


from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class SupportParserTPMYaml:
    def __init__(self, path: str):
        self.data = get_data_yaml(path)

    def process_property_fixed(
            self,
            result: SupportResultTPM,
            name: str,
            contents,
    ) -> None:
        result.name = name
        if "value" in contents:
            result.value = contents.get("value")
        else:
            result.value = contents.get("raw")

    def process_algorithms(
            self, result: SupportResultTPM, name: str, contents: int
    ) -> None:
        result.name = TPM2Identifier.ALG_ID_STR.get(contents)

    def process_commands(
            self, result: SupportResultTPM, name: str, contents: int
    ) -> None:
        result.name = TPM2Identifier.CC_STR.get(contents)

    def process_curves(
            self, result: SupportResultTPM, name: str, contents: int
    ) -> None:
        result.name = TPM2Identifier.ECC_CURVE_STR.get(contents)

    def process_capabilities(
            self, category, capabilities, profile, process_capability_f
    ):
        for key in capabilities:
            result = SupportResultTPM()
            result.category = category

            if isinstance(capabilities, dict):
                process_capability_f(result, key, capabilities[key])
            elif isinstance(capabilities, list):
                process_capability_f(result, key, key)

            profile.add_result(result)

    def parse(self) -> ProfileSupportTPM:
        profile = ProfileSupportTPM()

        data = self.data
        assert data

        capabilities = [
            ("Capability_properties-fixed", self.process_property_fixed),
            ("Capability_algorithms", self.process_algorithms),
            ("Capability_commands", self.process_commands),
            ("Capability_ecc-curves", self.process_curves),
        ]

        for name, handler in capabilities:
            if name in data:
                entry = data.pop(name)
                if entry is not None:
                    self.process_capabilities(name, entry, profile, handler)

        # Remaining data is put into test info dictionary
        profile.test_info = data

        return profile


class SupportParserTPMQuicktestYAML:
    """
    Class which parses support profile out of several, other files
    located in the detail directory of the measurement,
    """
    QUICKTEST_ALGORITHMS = "Quicktest_algorithms.txt"
    QUICKTEST_COMMANDS = "Quicktest_commands.txt"
    QUICKTEST_ECC_CURVES = "Quicktest_ecc-curves.txt"
    QUICKTEST_PROPERTIES_FIXED = "Quicktest_properties-fixed.txt"
    QUICKTEST_PROPERTIES_VARIABLE = "Quicktest_properties-variable.txt"

    def __init__(self, path: str, strict: bool):
        """
        Constructor for Quicktest parser
        :param path: path to the `detail` folder
        """
        path = os.path.join(path)
        assert os.path.exists(path)
        self.path = path
        self.strict = strict

    def parse_generic(self, profile: ProfileSupportTPM, filename: str,
                      projector: Callable[[Any, Any], int | str]):
        path = os.path.join(self.path, filename)
        assert os.path.exists(path)

        data = get_data_yaml(path)
        for key, value in data.items():
            result = SupportResultTPM()
            result.name = projector(key, value)
            result.value = value["value"] if value.get("value") else value.get(
                "raw")
            result.other = value
            assert result.name
            profile.add_result(result)

    def parse_properties_fixed(self, profile: ProfileSupportTPM):
        def projector(k, v):
            return k

        self.parse_generic(
            profile,
            SupportParserTPMQuicktestYAML.QUICKTEST_PROPERTIES_FIXED,
            projector
        )

    def parse_properties_variable(self, profile: ProfileSupportTPM):
        def projector(k, v):
            return k

        self.parse_generic(
            profile,
            SupportParserTPMQuicktestYAML.QUICKTEST_PROPERTIES_VARIABLE,
            projector
        )

    def parse_algorithms(self, profile: ProfileSupportTPM):
        def projector(k, v):
            return TPM2Identifier.ALG_ID_STR.get(v["value"])

        self.parse_generic(
            profile,
            SupportParserTPMQuicktestYAML.QUICKTEST_ALGORITHMS,
            projector
        )

    def parse_commands(self, profile: ProfileSupportTPM):
        def projector(k, v):
            return TPM2Identifier.CC_STR.get(v["commandIndex"])

        self.parse_generic(
            profile,
            SupportParserTPMQuicktestYAML.QUICKTEST_COMMANDS,
            projector
        )

    def parse_ecc_curves(self, profile: ProfileSupportTPM):
        def projector(k, v):
            return TPM2Identifier.ECC_CURVE_STR.get(v)

        self.parse_generic(
            profile,
            SupportParserTPMQuicktestYAML.QUICKTEST_ECC_CURVES,
            projector
        )

    def strict_check(self):
        assert os.path.exists(os.path.join(
            self.path, SupportParserTPMQuicktestYAML.QUICKTEST_ALGORITHMS))
        assert os.path.exists(os.path.join(
            self.path, SupportParserTPMQuicktestYAML.QUICKTEST_COMMANDS))
        assert os.path.exists(os.path.join(
            self.path,
            SupportParserTPMQuicktestYAML.QUICKTEST_PROPERTIES_FIXED))
        assert os.path.exists(os.path.join(
            self.path,
            SupportParserTPMQuicktestYAML.QUICKTEST_PROPERTIES_VARIABLE))
        assert os.path.exists(os.path.join(
            self.path, SupportParserTPMQuicktestYAML.QUICKTEST_ECC_CURVES))

    def parse(self) -> Optional[ProfileSupportTPM]:
        profile = ProfileSupportTPM()
        if self.strict:
            # Asserts invariants on Quicktest files existence
            self.strict_check()
        handles: List[Callable[[ProfileSupportTPM], None]] = [
            self.parse_properties_fixed, self.parse_properties_variable,
            self.parse_commands, self.parse_algorithms,
            self.parse_ecc_curves]

        for handle in handles:
            try:
                handle(profile)
            except:
                if self.strict:
                    return None

        if len(profile.results) == 0:
            return None
        return profile
