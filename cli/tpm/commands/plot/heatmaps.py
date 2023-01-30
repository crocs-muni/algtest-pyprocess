import csv
import os
from os import DirEntry
from typing import List, Tuple, Callable, Optional, Dict

import click
import pandas as pd

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from algtestprocess.modules.data.tpm.profiles.cryptoprops import CryptoProps
from algtestprocess.modules.visualization.heatmap import Heatmap

RSADataFrame = pd.DataFrame
DeviceName = str
Filename = str
PlotTitle = str


def plot_heatmap(
        df: RSADataFrame,
        device_name: DeviceName,
        title: PlotTitle,
        filename: Filename
):
    Heatmap(
        rsa_df=df,
        device_name=device_name,
        title=title
    ).build().save(
        filename
    )


def process_profile(
        root_path: str,
        dupes: Optional[Dict[str, int]] = None,
        algs: Optional[List[str]] = None,
) -> Optional[Tuple[
    CryptoProps,
    List[Tuple[
        CryptoPropResultCategory, RSADataFrame, DeviceName, Filename, PlotTitle]]
]]:
    cpps = TPMProfileManager(root_path).cryptoprops

    if not cpps:
        return None

    algs_to_prepare = [
        ("rsa-1024", CryptoPropResultCategory.RSA_1024),
        ("rsa-2048", CryptoPropResultCategory.RSA_2048)
    ]
    items = []
    device_name = cpps.device_name
    for alg_id, alg_enum in algs_to_prepare:
        if algs is None or alg_id in algs:
            # TODO: handle exception
            result = cpps.results.get(alg_enum)
            if not result:
                continue
            df = result.data
            # Drop unnecessary columns
            df = df.loc[:, ["n", "p", "q"]]
            idx = ''
            if dupes:
                dupes.setdefault(device_name, 0)
                dupes[device_name] += 1
                idx = '_{0:03}'.format(dupes[device_name])

            filename = f"heatmap_{device_name.replace(' ', '-')}_{idx}_{alg_id}.png"

            title = alg_id.upper().replace('-', ' ')
            items.append((alg_enum, df, device_name, filename, title))
    return cpps, items


@click.command()
@click.argument(
    'root_path',
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    default="."
)
@click.option(
    "--algs",
    type=click.Choice(["rsa-1024", "rsa-2048"], case_sensitive=False),
    default=None,
    nargs=1
)
@click.option(
    "--title",
    type=click.STRING,
    default=""
)
def heatmaps_single(root_path, output_path, algs, title):
    """
    Creates heatmaps describing the distribution between most significant
    bytes of RSA private primes, and modulus.

    ROOT_PATH is tpm2-algtest measurement folder root directory path,
    also known as the folder which has the following structure:

    \b
    . is the ROOT_PATH
    ./detail/ is REQUIRED folder
    ./performance.yaml
    ./results.yaml
    """
    _, items = process_profile(root_path, algs)
    for _, df, device_name, filename, title_suff in items:
        plot_heatmap(
            df,
            device_name,
            f"{title} {title_suff}",
            os.path.join(output_path, filename)
        )


Directory = str


def _walk(current_dir: Directory, depth: int) -> List[Directory]:
    """
    Tries to find all the paths for measurement folders

    Sentinel of the recursion is finding the directory with [Dd]etail folder

    :param current_dir: the directory we process now
    :return: list of paths to valid measurement folders
    """
    predicate: Callable[[DirEntry], bool] = \
        lambda x: x.is_dir() and x.name in {'detail', 'detail'}

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


@click.command()
@click.argument(
    'measurements_path',
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    default="."
)
@click.option(
    "--group-by-tpm",
    is_flag=True
)
@click.option(
    "--sort",
    is_flag=True
)
@click.option(
    "--title",
    type=click.STRING,
    default=""
)
def heatmaps_grouped(measurements_path, output_path, group_by_tpm, sort, title):
    """
    Creates heatmaps describing the distribution between most significant
    bytes of RSA private primes, and modulus. The output may be optionally
    merged by TPM device name. If you wanted to merge by HOST computer
    hostname, then you need to do it manually, that is divide the
    measurements into separate folders by HOST computer, then call
    this command on each individual folder of folders.

    MEASUREMENTS_FOLDER is a directory path containing tpm2-algtest
    measurement folders. There CANNOT be any more than 3 intermediate
    folders.
    """

    measurement_folders = _walk(measurements_path, 3)
    processed_profiles = filter(None, [
        process_profile(root_path, dupes={} if not group_by_tpm else None)
        for root_path in measurement_folders
    ])

    csv_data = {}
    if group_by_tpm:
        # By device name
        new = {}
        for p, items in processed_profiles:
            dn = p.device_name
            if new.get(dn) is None:
                new.setdefault(dn, (p, items))
                for alg_enum, curr_df, _, fname, _ in items:
                    path = p.results[alg_enum].path.replace(
                        measurements_path, ''
                    )
                    csv_data.setdefault((dn, alg_enum), [
                        p.manufacturer,
                        p.firmware_version,
                        len(curr_df),
                        fname, [path]])
            else:
                for idx, item in enumerate(items):
                    alg_enum, curr_df, _, filename, title_suff = item
                    other_df = new[dn][1][idx][1]
                    new_df = pd.concat([curr_df, other_df])
                    new[dn][1][idx] = \
                        (alg_enum, new_df, dn, filename, title_suff)

                    # Number of keys
                    csv_data[(dn, alg_enum)][2] = len(new_df)
                    path = p.results[alg_enum].path.replace(
                        measurements_path, ''
                    )
                    csv_data[(dn, alg_enum)][4].append(path)

        processed_profiles = list(new.values())

    if sort:
        # ProfileTPM has __eq__ and __lt__ which should be sufficient
        processed_profiles.sort()

    for cp, profile_items in processed_profiles:
        for _, df, device_name, filename, title_suff in profile_items:
            #print(list(cp.results.values())[0].path, len(df))
            plot_heatmap(
                df,
                device_name,
                f"{title} {len(df)} keys {title_suff}",
                os.path.join(output_path, filename)
            )
    if processed_profiles:
        values = list(csv_data.values())
        values.sort(key=lambda x: x[0])
        with open(os.path.join(output_path, 'heatmaps.csv'), 'w') as f:
            writer = csv.writer(f, delimiter=';', lineterminator='\n')
            writer.writerows(values)
