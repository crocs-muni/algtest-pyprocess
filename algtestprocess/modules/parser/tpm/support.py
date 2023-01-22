import re
from typing import Dict, List

from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.parser.tpm.utils import get_params
from algtestprocess.modules.tpmalgtest import ProfileSupportTPM, SupportResultTPM


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(filter(None, map(lambda x: x.strip(), data))), f.name.rsplit("/", 1)[1]


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
            match = re.search("(?P<name>TPM[2]?_PT.+);[ ]*(?P<value>[^\n]+)", lines[0])
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
                params.get("value") if params.get("value") else params.get("raw")
            )
            shift = 0
            # Each result can have up to 1 to 3 rows
            for key, _ in items:
                shift += 1 if params.get(key) else 0

            return shift
        return 1

    def parse_legacy(self):
        return self.parse(legacy=True)

    def parse(self, legacy: bool = False):
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
                profile.test_info[key] = val

            else:
                result = SupportResultTPM()
                val = None
                name = None
                current = current.replace(" ", "")

                if "properties-fixed" in category:
                    result.category = category
                    i += self.parse_props_fixed(lines[i : i + 3], result)
                    result.name = (
                        result.name.replace("TPM_", "TPM2_") if result.name else None
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
                        name = TPM2Identifier.ECC_CURVE_STR.get(int(current, 16))
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
        self.data = None
        with open(path) as f:
            self.data = load(f, Loader)
        assert self.data

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
                self.process_capabilities(name, entry, profile, handler)

        # Remaining data is put into test info dictionary
        profile.test_info = data

        return profile
