import os
from typing import List, Tuple, Callable, Union, Dict

from tqdm import tqdm

from algtestprocess.modules.jcalgtest import ProfileJC, PerformanceResultJC
from algtestprocess.modules.profiles.tpm.base import ProfileTPM

Name = str
Href = str
Profile = Union[ProfileJC, ProfileTPM]


def run_helper(
    output_path: str,
    profiles: List[Profile],
    run_single: Callable,
    desc: str = "Unknown",
) -> List[Tuple[Name, Href]]:
    """
    Function which repeatedly calls run_single method and saves
    the results of processing
    :return List of tuples used to reference created files
    """
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    data: List[Tuple[str, str]] = []
    for i in tqdm(range(len(profiles)), desc=desc):
        profile = profiles[i]
        name = profile.device_name()
        path = f"{output_path}/{name}.html"
        with open(path, "w") as f:
            f.write(run_single(profile=profile))
        data.append((name, path))
    return data


def run_helper_multi(
    output_path: str,
    items: List[List[Profile]],
    run_single: Callable,
    desc: str = "Unknown",
) -> Dict[Tuple[Profile, ...], str]:
    """
    Similar to run_helper method except for the fact it is called for
    list of the profiles. Used in comparison radar graphs.
    """
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    data: Dict[Tuple[Profile, ...], str] = {}
    for j in tqdm(range(len(items)), desc=desc):
        profiles = items[j]
        filename = ""
        for i, profile in enumerate(profiles):
            filename += ("_vs_" if i > 0 else "") + profile.device_name()
        path = f"{output_path}/{filename}.html"
        with open(path, "w") as f:
            f.write(run_single(profiles))
        data[tuple(profiles)] = filename
    return data


def results_map(r: List[PerformanceResultJC]):
    """Remove unsuccessfully measured results"""
    return list(
        filter(
            None, map(lambda x: x if x.error == "OK" and x.data_length > 0 else None, r)
        )
    )


def filtered_results(items: List[Tuple[str, List[PerformanceResultJC]]]):
    """
    Filters empty lists of results
    """
    return list(filter(lambda x: x[1], map(lambda i: (i[0], results_map(i[1])), items)))
