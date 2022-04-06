import re
from typing import List, Tuple, Optional


def get_params(line: str, items: List[Tuple[str, str]]):
    """
    Function which returns dictionary with found patterns content.
    """
    return dict([
        (key, s.group(key))
        for key, s in [(k, re.search(rgx, line)) for k, rgx in items] if s
    ])


def to_int(item: Optional[str], base: int):
    return int(item, base) if item else None