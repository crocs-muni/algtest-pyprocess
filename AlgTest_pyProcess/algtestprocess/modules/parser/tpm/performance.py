import re
from typing import List, Tuple

from algtestprocess.modules.tpmalgtest import ProfilePerformanceTPM, \
    PerformanceResultTPM


def get_data(path: str):
    with open(path) as f:
        data = f.readlines()
    return list(map(lambda x: x.strip(), data))


def get_params(line: str, items: List[Tuple[str, str]]):
    return dict([
        (key, s.group(key))
        for key, s in [(k, re.search(rgx, line)) for k, rgx in items] if s
    ])


class PerformanceParserTPM:
    def __init__(self, path: str):
        self.lines = list(filter(None, get_data(path)))

    @staticmethod
    def parse_parameters(line: str, result: PerformanceResultTPM):
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
        print(params)
        result.algorithm = params.get("algorithm")
        result.key_length = params.get("key_length")
        result.mode = params.get("mode")
        result.encrypt_decrypt = params.get("encrypt_decrypt")
        result.data_length = params.get("data_length")
        result.key_params = params.get("key_params")
        result.scheme = params.get("scheme")

    @staticmethod
    def parse_operation(line: str, result: PerformanceResultTPM):
        items = [
            ("op_avg", r"avg op:;(?P<op_avg>[0-9]+\.[0-9]+)"),
            ("op_min", r"min op:;(?P<op_min>[0-9]+\.[0-9]+)"),
            ("op_max", r"max op:;(?P<op_max>[0-9]+\.[0-9]+)")
        ]
        params = get_params(line, items)
        print(params)
        result.operation_min = params["op_min"]
        result.operation_avg = params["op_avg"]
        result.operation_max = params["op_max"]

    @staticmethod
    def parse_info(line: str, result: PerformanceResultTPM):
        items = [
            ("iterations", r"total iterations:;(?P<iterations>[0-9]+)"),
            ("successful", r"successful:;(?P<successful>[0-9]+\.[0-9]+)"),
            ("failed", r"failed:;(?P<failed>[0-9]+)"),
            ("error", r"error:;(?P<error>(None|[0-9a-fA-F]+))")
        ]
        params = get_params(line, items)
        print(params)
        result.iterations = params.get("iterations")
        result.successful = params.get("successful")
        result.failed = params.get("failed")
        result.error = params.get("error")

    def parse(self):
        category = None
        profile = ProfilePerformanceTPM()
        lines = self.lines
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
                PerformanceParserTPM.parse_parameters(lines[i], result)
                PerformanceParserTPM.parse_operation(lines[i + 1], result)
                PerformanceParserTPM.parse_info(lines[i + 2], result)
                profile.results.append(result)
                i = i + 2
            i = i + 1
        return profile
