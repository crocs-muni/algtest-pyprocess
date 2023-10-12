import os
from os import DirEntry
import re
from typing import Callable, List, Tuple, Optional



def get_params(line: str, items: List[Tuple[str, str]]):
    """
    Function which returns dictionary with found patterns content.
    """
    return dict([
        (key, s.group(key))
        for key, s in [(k, re.search(rgx, line)) for k, rgx in items] if s
    ])


def parse_ek(ek):
    # Actual EK may look like yaml, but yaml parser does not work
    rgx = r"n prefix: ([a-f0-9]+)\s*n suffix: ([a-f0-9]+)$"
    result = re.search(rgx, ek, flags=re.MULTILINE)
    if result is None:
        return None
    return int(result.group(1), 16), int(result.group(2), 16)


def get_ek_msb(ek):
    if isinstance(ek, str):
        return [parse_ek(ek)[0] >> 8]
    elif isinstance(ek, list):
        return [parse_ek(x)[0] >> 8 for x in ek]
    return []


def to_int(item: Optional[str], base: int):
    return int(item, base) if item else None


Directory = str


def _walk(current_dir: Directory, depth: int) -> List[Directory]:
    """
    Tries to find all the paths for measurement folders

    Sentinel of the recursion is finding the directory with [Dd]etail folder

    :param current_dir: the directory we process now
    :return: list of paths to valid measurement folders
    """
    predicate: Callable[[DirEntry], bool] = lambda x: x.is_dir() and x.name in {
        "detail",
        "Detail",
    }

    scan: List[DirEntry] = list(os.scandir(current_dir))

    if any([predicate(entry) for entry in scan]):
        return [current_dir]

    if depth <= 0:
        return []

    result = []
    for entry in scan:
        if entry.is_dir():
            result += _walk(entry.path, depth - 1)

    return result
