import re

from algtestprocess.modules.config import TPM2Identifier
from algtestprocess.modules.parser.tpm.utils import get_params, to_int
from algtestprocess.modules.tpmalgtest import ProfilePerformanceTPM, \
    PerformanceResultTPM


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(map(lambda x: x.strip(), data)), f.name.rsplit("/", 1)[1]


def get_algorithm(algorithm: str):
    if algorithm and re.match(r"0x[0-9a-f]+", algorithm):
        return TPM2Identifier.ALG_ID_STR.get(int(algorithm, 16))
    return algorithm


def get_key_params(key_params: str):
    if key_params and re.match(r"ECC 0x[0-9a-f]+", key_params):
        key_params = to_int(key_params.split()[1], 16)
        return TPM2Identifier.ECC_CURVE_STR[key_params]
    if key_params and re.match(r"SYMCIPHER 0x[0-9a-f]+", key_params):
        key_params = key_params.split()
        alg = to_int(key_params[1], 16)
        return f"{TPM2Identifier.ALG_ID_STR[alg]} {key_params[2]}"
    return key_params


class PerformanceParserTPM:
    def __init__(self, path: str):
        self.lines, self.filename = list(filter(None, get_data(path)))

    @staticmethod
    def parse_parameters(line: str, result: PerformanceResultTPM):
        """Parsing section with parameters using regular expressions"""

        items = [
            ("algorithm",
             r"(Algorithm|Hash algorithm):;(?P<algorithm>(0x[0-9a-fA-F]+))"),
            ("key_length", r"Key length:;(?P<key_length>[0-9]+)"),
            ("mode", r"Mode:;(?P<mode>0x[0-9a-fA-F]+)"),
            ("encrypt_decrypt", r"Encrypt/decrypt\?:;(?P<encrypt_decrypt>\w+)"),
            ("data_length", r"Data length \(bytes\):;(?P<data_length>[0-9]+)"),
            ("key_params", r"Key parameters:;(?P<key_params>[^;$]+)"),
            ("scheme", r"\Scheme:;(?P<scheme>0x[0-9a-fA-F]+)")
        ]
        params = get_params(line, items)
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
            ("op_avg", r"avg op:;(?P<op_avg>[0-9]+\.[0-9]+)"),
            ("op_min", r"min op:;(?P<op_min>[0-9]+\.[0-9]+)"),
            ("op_max", r"max op:;(?P<op_max>[0-9]+\.[0-9]+)")
        ]
        params = get_params(line, items)
        result.operation_min = float(params["op_min"])
        result.operation_avg = float(params["op_avg"])
        result.operation_max = float(params["op_max"])

    @staticmethod
    def parse_info(line: str, result: PerformanceResultTPM):
        """Parsing section with test information using regular expressions"""
        items = [
            ("iterations", r"total iterations:;(?P<iterations>[0-9]+)"),
            ("successful", r"successful:;(?P<successful>[0-9]+\.[0-9]+)"),
            ("failed", r"failed:;(?P<failed>[0-9]+)"),
            ("error", r"error:;(?P<error>(None|[0-9a-fA-F]+))")
        ]
        params = get_params(line, items)
        result.iterations = to_int(params.get("iterations"), 10)
        result.successful = to_int(params.get("successful"), 10)
        result.failed = to_int(params.get("failed"), 10)
        result.error = params.get("error")

    def parse(self):
        category = None
        profile = ProfilePerformanceTPM()
        profile.test_info['TPM name'] = self.filename.replace(".csv", "")
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
