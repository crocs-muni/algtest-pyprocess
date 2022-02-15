import os
from typing import List, Tuple, Callable

from algtestprocess.modules.jcalgtest import ProfileJC, PerformanceResultJC

Name = str
Href = str


def run_helper(
        output_path: str, profiles: List[ProfileJC], run_single: Callable
) -> List[Tuple[Name, Href]]:
    """
    Function which repeatedly calls run_single method and saves
    the results of processing
    :return List of tuples used to reference created files
    """
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    data: List[Tuple[str, str]] = []
    for profile in profiles:
        name = profile.test_info["Card name"]
        filename = name.replace(" ", "")
        path = f"{output_path}/{filename}.html"
        with open(path, "w") as f:
            f.write(run_single(profile))
        data.append((name, path))
    return data


def results_map(r: List[PerformanceResultJC]):
    """Remove unsuccessfully measured results"""
    return list(
        filter(None,
               map(lambda x:
                   x if x.status == "OK" and x.data_length > 0 else None, r)))


def filtered_results(items: List[Tuple[str, List[PerformanceResultJC]]]):
    """
    Function which filters results which are not successfully measured
    """
    return list(
        filter(lambda x: x[1], map(lambda i: (i[0], results_map(i[1])), items)))
