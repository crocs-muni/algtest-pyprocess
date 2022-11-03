from typing import List, Union, Dict
import pandas as pd


def merge_cryptoprops_dfs(profiles: List[Dict[str, Union[str, any]]], algs: List[str]):
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
