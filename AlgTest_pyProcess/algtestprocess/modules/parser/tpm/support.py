from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.tpmalgtest import ProfileSupportTPM, \
    SupportResultTPM


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(filter(None, map(lambda x: x.strip(), data)))


class SupportParserTPM:
    def __init__(self, path: str):
        self.lines = get_data(path)

    def parse(self):
        profile = ProfileSupportTPM()
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

                if category == "Quicktest_properties-fixed":
                    splits = current.split(";", 1)
                    name = splits[0]
                    val = splits[1] if len(splits) > 1 else None

                elif category == "Quicktest_algorithms":
                    name = TPM2Identifier.ALG_ID_STR.get(int(current, 16))

                elif category == "Quicktest_commands":
                    name = TPM2Identifier.CC_STR.get(int(current, 16))

                elif category == "Quicktest_ecc-curves":
                    name = TPM2Identifier.ECC_CURVE_STR.get(int(current, 16))

                result.category = category
                result.name = name
                result.value = val

                profile.add_result(result)
            i += 1
        return profile
