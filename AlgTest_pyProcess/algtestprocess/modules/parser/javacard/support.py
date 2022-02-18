import re

from algtestprocess.modules.jcalgtest import ProfileSupportJC, SupportResultJC


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(filter(None, map(lambda x: x.strip(), data))), \
           f.name.rsplit("/", 1)[1]


def satinize_category(category: str):
    to_remove = ["\\", ",", ";", "Class ", ";supported", ",supported,time"]
    for word in to_remove:
        category = category.replace(word, "")
    return category


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


def add_additional_test_info(profile: ProfileSupportJC, filename):
    profile.test_info["Github link"] = \
        "https://github.com/crocs-muni/jcalgtest_results/blob/main/javacard/Profiles/results/" +\
        filename.replace(" ", "")


class SupportParserJC:
    """Data parsing from csv support results for javacards"""
    ADDITIONAL_TEST_INFO = [
        "Available RAM memory",
        "Available EEPROM memory",
        "Available RAM memory",
        "Total test time"
    ]

    def __init__(self, path: str):
        self.lines, self.filename = get_data(path)

    def parse(self):
        category = None
        profile = ProfileSupportJC()
        lines = self.lines
        i = 0
        destinations = [
            (["JCSystem", "APDU"], profile.jcsystem),
            (["CPLC"], profile.cplc),
            (["INFO:"], {}),
            ([""], profile.test_info)
        ]

        # Named constants for fields while splitting
        NAME = 0
        SUPPORT = 1
        TIME_ELAPSED = 2
        PERSISTENT_MEMORY = 3
        RAM_DESELECT = 4
        RAM_RESET = 5

        while i < len(lines):
            current = lines[i]
            if "javacard." in current or "javacardx." in current:
                category = satinize_category(current)

            # Specific category which needed to be addressed explicitly.
            elif "Support for variable public exponent for RSA 1024" in current:
                category = "Variable RSA 1024"

            elif not category:
                for tests, destination in destinations:
                    if any(list(map(lambda x: x in current, tests))):
                        key, value = re.split(r"[;,]", current, maxsplit=1)
                        destination[key] = value

            else:
                # Put specific lines into test_info
                misplaced = any([
                    x in current for x in SupportParserJC.ADDITIONAL_TEST_INFO
                ])
                if misplaced:
                    key, value = re.split(r"[;,]", current, maxsplit=1)
                    profile.test_info[key] = value
                    i += 1
                    continue

                current = list(filter(None, re.split(r"[;,]", current)))

                if len(current) < 2:
                    i += 1
                    continue

                result = SupportResultJC()
                result.name = current[NAME].strip()
                result.category = category

                if current[SUPPORT] in ["yes", "no"]:
                    result.support = current[SUPPORT] == "yes"
                    result.status = "OK"
                else:
                    result.status = current[SUPPORT]

                if len(current) > TIME_ELAPSED and \
                        re.match(r"\d+\.\d+", current[TIME_ELAPSED]):
                    result.time_elapsed = float(
                        current[TIME_ELAPSED].split()[0].rsplit(".")[0]
                    )

                if len(current) > PERSISTENT_MEMORY:
                    result.persistent_memory = int(
                        current[PERSISTENT_MEMORY].split()[0]
                    )

                if len(current) > RAM_DESELECT:
                    result.ram_deselect = int(current[RAM_DESELECT])

                if len(current) > RAM_RESET:
                    result.ram_reset = int(current[RAM_RESET])
                profile.add_result(result.name, result)

            i += 1

        parse_name_provider_atr(profile, self.filename)
        add_additional_test_info(profile, self.filename)
        return profile
