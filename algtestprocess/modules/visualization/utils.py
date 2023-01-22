from typing import List, Tuple, Union, Dict, Optional
import pandas as pd

Item = Tuple[pd.DataFrame, Optional[str], str]


def merge_cryptoprops_dfs(
    profiles: List[Dict[str, str | pd.DataFrame]], algs: List[str]
) -> Tuple[List[Item], List[Item]]:
    """
    Function which merges the Cryptoprops profiles of identical devices by algorithm
    :param profiles: List of Cryptoprops profiles
    :returns: Tuple of lists of Items ->  (dataframe, device_name, algorithm)
    """
    items_base = [
        (profile.get(alg), profile.get("device_name"), alg)
        for alg in algs
        for profile in profiles
    ]

    items_merged = {}
    for alg in algs:
        items_by_alg = [item for item in items_base if item[2] == alg]
        for df, device_name, _ in items_by_alg:
            key = (device_name, alg)
            items_merged.setdefault(key, [])
            if df is not None:
                items_merged[key].append(df)
    items_merged = [
        (
            (pd.concat(dfs), f"{device_name} {alg} MERGED", alg)
            if len(dfs) > 1
            else (dfs[0], f"{device_name} {alg}", alg)
        )
        for (device_name, alg), dfs in items_merged.items()
        if dfs
    ]
    return items_base, items_merged
