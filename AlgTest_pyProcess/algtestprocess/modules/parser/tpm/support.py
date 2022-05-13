import re
from typing import List

from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.parser.tpm.utils import get_params
from algtestprocess.modules.tpmalgtest import ProfileSupportTPM, \
    SupportResultTPM


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(filter(None, map(lambda x: x.strip(), data))), \
           f.name.rsplit("/", 1)[1]


class SupportParserTPM:
    """
    TPM support profile parser
    Note: reads CSV support profiles for TPMs
    """
    def __init__(self, path: str):
        self.lines, self.filename = get_data(path)

    def parse_props_fixed(self, lines: List[str], result: SupportResultTPM):
        """Parse fixed properties section"""
        joined = '\n'.join(lines)

        if "raw" not in joined and lines:
            match = re.search("(?P<name>TPM[2]?_PT.+);[ ]*(?P<value>[^\n]+)", lines[0])
            if not match:
                return 1
            result.name = match.group("name")
            result.value = match.group("value")

        else:
            items = [
                ("name", "(?P<name>TPM[2]?_PT.+);"),
                ("raw", "raw;[ ]*(?P<raw>0[x]?[0-9a-fA-F]*)"),
                ("value", "value;[ ]*(?P<value>\".*\")")
            ]
            params = get_params(joined, items)
            result.name = params.get("name")
            result.value = params.get("value") \
                if params.get("value") else params.get("raw")
            shift = 0
            # Each result can have up to 1 to 3 rows
            for key, _ in items:
                shift += 1 if params.get(key) else 0
            return shift
        return 1

    def parse(self):
        profile = ProfileSupportTPM()
        profile.test_info['TPM name'] = self.filename.replace(".csv", "")
        lines = self.lines
        category = None
        i = 0
        while i < len(self.lines):
            current = lines[i]
            if "Quicktest" in current:
                category = current

            elif not category:
                key, val = current.split(";", 1)
                profile.test_info[key] = val

            else:
                result = SupportResultTPM()
                val = None
                name = None
                current = current.replace(" ", "")

                if "properties-fixed" in category:
                    result.category = category
                    i += self.parse_props_fixed(lines[i:i+3], result)
                    result.name = result.name.replace("TPM_", "TPM2_") \
                        if result.name else None
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
