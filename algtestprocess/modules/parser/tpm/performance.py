import re

from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.data.tpm.profiles.performance import \
    ProfilePerformanceTPM
from algtestprocess.modules.data.tpm.results.performance import \
    PerformanceResultTPM
from algtestprocess.modules.parser.tpm.utils import get_params, to_int


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(map(lambda x: x.strip(), data)), f.name.rsplit("/", 1)[1]


def get_algorithm(algorithm: str):
    if algorithm and re.match(r"0x[0-9a-f]+", algorithm):
        return TPM2Identifier.ALG_ID_STR.get(int(algorithm, 16))
    return algorithm


def get_key_params(key_params: str):
    """Helper for correctly parsing key params section of result"""
    if key_params and re.match(r"ECC 0x[0-9a-f]+", key_params):
        key_params = to_int(
            re.search(r"(0x[a-fA-F0-9]+)", key_params.split()[1]).group(0), 16
        )
        return TPM2Identifier.ECC_CURVE_STR[key_params]
    if key_params and re.match(r"SYMCIPHER 0x[0-9a-f]+", key_params):
        key_params = key_params.split()
        alg = to_int(key_params[1], 16)
        return f"{TPM2Identifier.ALG_ID_STR[alg]} {key_params[2]}"
    return key_params


def get_offset(lines, i):
    """Measure offset to next entry or EOF"""
    j = 1
    while i + j < len(lines):
        if "TPM2_" in lines[i + j]:
            return j
        j += 1
    return -1


class PerformanceParserTPM:
    """TPM performance profile parser"""

    def __init__(self, path: str):
        self.lines, self.filename = list(filter(None, get_data(path)))

    @staticmethod
    def parse_parameters(line: str, result: PerformanceResultTPM):
        """Parsing section with parameters using regular expressions"""

        items = [
            ("category", r"(?P<category>TPM2_.+):"),
            (
                "algorithm",
                r"(Algorithm|[Hh]ash algorithm):[; ](?P<algorithm>(0x[0-9a-fA-F]+))",
            ),
            ("key_length", r"Key length:;(?P<key_length>[0-9]+)"),
            ("mode", r"Mode:;(?P<mode>0x[0-9a-fA-F]+)"),
            ("encrypt_decrypt", r"Encrypt/decrypt\?:;(?P<encrypt_decrypt>\w+)"),
            ("data_length",
             r"[Dd]ata length \(bytes\):[; ](?P<data_length>[0-9]+)"),
            ("key_params", r"[Kk]ey parameters:[; ](?P<key_params>[^;$\n]+)"),
            ("scheme", r"[\Ss]cheme:[; ](?P<scheme>0x[0-9a-fA-F]+)"),
        ]
        params = get_params(line, items)
        result.category = params.get("category")
        result.algorithm = get_algorithm(params.get("algorithm"))
        result.key_length = to_int(params.get("key_length"), 10)
        result.mode = get_algorithm(params.get("mode"))
        result.encrypt_decrypt = params.get("encrypt_decrypt")
        result.data_length = to_int(params.get("data_length"), 10)
        result.key_params = get_key_params(params.get("key_params"))
        result.scheme = get_algorithm(params.get("scheme"))

    @staticmethod
    def parse_operation(line: str, result: PerformanceResultTPM):
        """Parsing section with operation times using regular expressions"""
        items = [
            ("op_avg", r"avg op:[; ](?P<op_avg>[0-9]+\.[0-9]+)"),
            ("op_min", r"min op:[; ](?P<op_min>[0-9]+\.[0-9]+)"),
            ("op_max", r"max op:[; ](?P<op_max>[0-9]+\.[0-9]+)"),
        ]
        params = get_params(line, items)
        result.operation_min = float(params["op_min"])
        result.operation_avg = float(params["op_avg"])
        result.operation_max = float(params["op_max"])

    @staticmethod
    def parse_info(line: str, result: PerformanceResultTPM):
        """Parsing section with test information using regular expressions"""
        items = [
            ("iterations", r"total iterations:[; ](?P<iterations>[0-9]+)"),
            ("successful", r"successful:[; ](?P<successful>[0-9]+)"),
            ("failed", r"failed:[; ](?P<failed>[0-9]+)"),
            ("error", r"error:[; ](?P<error>(None|[0-9a-fA-F]+))"),
        ]
        params = get_params(line, items)
        result.iterations = to_int(params.get("iterations"), 10)
        result.successful = to_int(params.get("successful"), 10)
        result.failed = to_int(params.get("failed"), 10)
        result.error = params.get("error")

    def parse(self):
        try:
            profile = self._parse()
        except:
            try:
                profile = self._parse_legacy()
            except:
                return None
        if not profile.results:
            return None
        return profile

    def _parse(self):
        parsed_testinfo = False
        lines = list(filter(None, self.lines))
        profile = ProfilePerformanceTPM()
        i = 0
        while i < len(lines):
            offset = 1
            if "TPM2_" in lines[i]:
                parsed_testinfo = True
                result = PerformanceResultTPM()
                offset = get_offset(lines, i)
                entry = "\n".join(
                    lines[i:] if offset == -1 else lines[i: i + offset])
                PerformanceParserTPM.parse_info(entry, result)
                PerformanceParserTPM.parse_parameters(entry, result)
                PerformanceParserTPM.parse_operation(entry, result)
                profile.add_result(result)

            if not parsed_testinfo and len(lines) > 0:
                key, val = list(
                    map(lambda x: x.strip(), lines[i].split(":", maxsplit=1))
                )
                profile.test_info[key] = val

            if offset == -1:
                break

            i += offset
        return profile

    def _parse_legacy(self):
        category = None
        profile = ProfilePerformanceTPM()
        lines = list(filter(None, self.lines))
        i = 0
        while i < len(lines):
            items = lines[i].split(";", 1)
            if not category and len(items) > 1:
                key, val = items
                profile.test_info[key] = val.strip()
            if len(items) == 1:
                category = items[0]
                i = i + 1
            if category and i + 2 < len(lines):
                result = PerformanceResultTPM()
                result.category = category
                PerformanceParserTPM.parse_parameters(lines[i], result)
                PerformanceParserTPM.parse_operation(lines[i + 1], result)
                PerformanceParserTPM.parse_info(lines[i + 2], result)
                profile.add_result(result)
                i = i + 2
            i = i + 1
        return profile


from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class PerformanceParserTPMYaml:
    def __init__(self, path: str):
        self.data = None
        with open(path) as f:
            self.data = load(f, Loader)
        assert self.data

    def process_key_params(self, result: PerformanceResultTPM, contents):
        result.key_params = contents.get("key parameters")

    def process_data_length(self, result: PerformanceResultTPM, contents):
        result.data_length = contents.get("data length (bytes)")

    def process_hash_algorithm(self, result: PerformanceResultTPM, contents):
        ha = contents.get("hash algorithm")
        assert ha
        if isinstance(ha, int):
            result.algorithm = TPM2Identifier.ALG_ID_STR[ha]
        else:
            # Some entries, have filled in string like SHA-256 instead of numeric id
            result.algorithm = "TPM2_ALG_" + ha.replace("-", "")

    def process_scheme(self, result: PerformanceResultTPM, contents):
        scheme = contents.get("scheme")
        assert scheme and isinstance(scheme, int)
        result.scheme = TPM2Identifier.ALG_ID_STR[scheme]

    def process_op_stats(self, result: PerformanceResultTPM, contents):
        stats = contents.get("operation stats (ms/op)")
        assert stats
        result.operation_min = float(stats["min op"])
        result.operation_avg = float(stats["avg op"])
        result.operation_max = float(stats["max op"])

    def process_op_info(self, result: PerformanceResultTPM, contents):
        info = contents.get("operation info")
        assert info
        result.iterations = int(info["total iterations"])
        result.successful = int(info["successful"])
        result.failed = int(info["failed"])
        result.error = info["error"]

    def process_entry(
            self, result: PerformanceResultTPM, category: str, contents: dict
    ):
        assert isinstance(contents, dict)
        # All entries contain Operation Stats, and Operatien Info
        # Optional entries are command dependant
        # (kparams, data_length, hash_algorithm, scheme)
        entry_contents = {
            "TPM2_Create": (True, False, False, False),
            "TPM2_GetRandom": (False, True, False, False),
            "TPM2_HMAC": (False, True, True, False),
            "TPM2_Hash": (False, True, True, False),
            "TPM2_RSA_Decrypt": (True, False, False, True),
            "TPM2_RSA_Encrypt": (True, False, False, True),
            "TPM2_Sign": (True, False, False, True),
            "TPM2_VerifySignature": (True, False, False, True),
            "TPM2_ZGen": (True, False, False, True),
        }

        self.process_op_stats(result, contents)
        self.process_op_info(result, contents)

        handlers = [
            self.process_key_params,
            self.process_data_length,
            self.process_hash_algorithm,
            self.process_scheme,
        ]

        for i in range(len(handlers)):
            if entry_contents.get(category)[i]:
                handlers[i](result, contents)

    def process_tpm_commands(
            self, profile: ProfilePerformanceTPM, category: str, entries
    ):
        for sub in entries:
            result = PerformanceResultTPM()
            result.category = category

            if isinstance(entries, dict):
                self.process_entry(result, category, entries[sub])
            elif isinstance(entries, list):
                self.process_entry(result, category, sub)

            profile.add_result(result)

    def parse(self) -> ProfilePerformanceTPM:
        profile = ProfilePerformanceTPM()

        data = self.data
        assert data

        categories = [
            "TPM2_Create",
            "TPM2_GetRandom",
            "TPM2_HMAC",
            "TPM2_Hash",
            "TPM2_RSA_Decrypt",
            "TPM2_RSA_Encrypt",
            "TPM2_Sign",
            "TPM2_VerifySignature",
            "TPM2_ZGen",
        ]

        for category in categories:
            if category in data:
                entries = data.pop(category)
                self.process_tpm_commands(profile, category, entries)

        # Remaining data is put into test info dictionary
        profile.test_info = data

        return profile
