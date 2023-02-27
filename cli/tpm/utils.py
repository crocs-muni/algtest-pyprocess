import os
from os import DirEntry
from typing import List, Callable

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
