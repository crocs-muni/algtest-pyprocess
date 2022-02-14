import re

from algtestprocess.modules.jcalgtest import ProfileSupportJC, SupportResultJC


def get_data(path: str):
    with open(path) as f:
        data = f.read()
    return data, f.name.rsplit("/", 1)[1]


def parse_name_provider_atr(profile: ProfileSupportJC, filename: str):
    filename = filename.replace("_ALGSUPPORT_", "")

    for sub in ["_3B ", "_3b ", "_3B_", "_3b_"]:
        atr_index = filename.find(sub)
        if atr_index != -1:
            break

    card_name = filename[:atr_index]
    provided_index = filename.find("(provided")
    atr, provided = "", ""
    if provided_index != -1:
        atr = filename[atr_index:provided_index]
        provided = filename[provided_index:].rstrip(".csv")

    card_name = card_name.replace("_", " ")
    atr = atr.replace("_", " ").strip()
    provided = provided.replace("_", " ")

    profile.test_info["Card name"] = card_name
    profile.test_info["Card ATR"] = atr
    profile.test_info["Provider"] = provided


class SupportParser:
    ADDITIONAL_TEST_INFO = [
        "Available RAM memory",
        "Available EEPROM memory",
        "Available RAM memory",
        "Total test time"
    ]

    def __init__(self, path: str):
        self.data, self.filename = get_data(path)

    def parse(self, profile: ProfileSupportJC):
        info_parsed = False
        for line in self.data.split("\n"):
            if not line:
                continue
            if "JCSystem" in line or "APDU" in line:
                key, value = line.split(";", 1)
                profile.jcsystem[key] = value.strip()
            elif "CPLC" in line:
                key, value = line.split(";", 1)
                profile.cplc[key] = value.strip()
            elif "javacard." in line or "javacardx." in line:
                info_parsed = True
                category = line\
                    .replace("\\", "").strip(",").strip(";")\
                .replace("Class ", "").replace(";supported", "")\
                .replace(",supported,time", "").strip()
            elif "variable public exponent for RSA 1024" in line:
                category = "Variable RSA 1024 - support for variable public " \
                           "exponent. If supported, user-defined fast " \
                           "modular exponentiation can be executed on the " \
                           "smart card via cryptographic coprocessor. This " \
                           "is very specific feature and you will probably " \
                           "not need it"
            else:
                misplaced = any([
                    x in line for x in SupportParser.ADDITIONAL_TEST_INFO
                ])
                if not info_parsed or misplaced:
                    key, value = re.split(r"[;,]", line, maxsplit=1)
                    profile.test_info[key] = value
                else:
                    line = list(filter(None, re.split(r"[;,]", line)))
                    if not line or len(line) < 2:
                        continue
                    result = SupportResultJC()
                    result.category = category
                    result.name = line[0].strip()
                    if line[1] in ["yes", "no"]:
                        result.support = line[1] == "yes"
                        result.status = "OK"
                    else:
                        result.status = line[1]
                    if len(line) > 2 and re.match(r"\d+\.\d+", line[2]):
                        line[2] = line[2].split()[0].rsplit(".", 1)[0]
                        result.time_elapsed = float(line[2])
                    if len(line) > 3 and line[3]:
                        line[3] = line[3].split()[0]
                        result.persistent_memory = int(line[3])
                    if len(line) > 4 and line[4]:
                        result.ram_deselect = int(line[4])
                    if len(line) > 5 and line[5]:
                        result.ram_reset = int(line[5])
                    profile.add_result(result.name, result)
        parse_name_provider_atr(profile, self.filename)
        profile.test_info["Github link"] = \
            "https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/" + self.filename
        return profile
