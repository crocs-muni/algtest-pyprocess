import json
import os.path
from datetime import datetime

import click
import pandas as pd
from checksumdir import dirhash

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from cli.tpm.utils import _walk

Path = str


def sum_up(measurement_folder: Path, data) -> None:
    # TODO: What needs to be in summary ?
    man = TPMProfileManager(measurement_folder)
    cpps = man.cryptoprops

    if cpps:
        tpm_name = f"{cpps.manufacturer} {cpps.firmware_version}"
    elif man.support_profile:
        tpm_name = f"{man.support_profile.manufacturer} " \
                   f"{man.support_profile.firmware_version}"
    elif man.performance_profile:
        tpm_name = f"{man.performance_profile.manufacturer} " \
                   f"{man.performance_profile.firmware_version}"
    else:
        return

    # number of keypairs/signatures per algorithm is assumed to be the same
    kpairs = None
    generated_keypairs = 0

    signatures = None
    created_signatures = 0

    if cpps:
        signatures = cpps.results.get(CryptoPropResultCategory.ECC_P256_ECDAA)
        kpairs = cpps.results.get(CryptoPropResultCategory.RSA_1024)

        if signatures:
            created_signatures = len(signatures.data)
            del signatures.data

        if kpairs:
            generated_keypairs = len(kpairs.data)
            del kpairs.data


    try:
        rng_data_collected = os.path.getsize(
            os.path.join(measurement_folder, 'detail/Rng.bin')
        )
    except FileNotFoundError:
        rng_data_collected = 0

    date = None
    if man.support_profile:
        date = datetime.strptime(
            man.support_profile.test_info['Execution date/time'],
            '%Y/%m/%d %H:%M:%S'
        )

    if data.get(tpm_name) is None:
        data[tpm_name] = {
            "TPM name": tpm_name,
            "total measurements": 1,
            "date": date.strftime('%Y/%m/%d %H:%M:%S') if date else '-',
            "keypairs generated": generated_keypairs,
            "signatures created": created_signatures,
            "rng data collected": rng_data_collected,
        }
    else:
        data[tpm_name]["total measurements"] += 1
        data[tpm_name]["keypairs generated"] += generated_keypairs
        data[tpm_name]["signatures created"] += created_signatures
        data[tpm_name]["rng data collected"] += rng_data_collected


@click.command()
@click.argument("measurements_path",
                type=click.Path(exists=True, dir_okay=True))
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    default=".",
)
@click.option(
    "-i",
    "--prev-summary-path",
    type=click.Path(file_okay=True, dir_okay=False, writable=True)
)
@click.option("--hash-file", required=False, default=None,
              type=click.Path(exists=True, file_okay=True))
def summary_update(measurements_path, output_path, prev_summary_path, hash_file):
    measurement_folders = _walk(measurements_path, 3)

    # The hash file is used to take note of which measurements it was accounted
    # for in the summary
    hashes = set()
    if hash_file is not None:
        with open(hash_file, "r") as f:
            hashes = set(json.load(f))

    # If we already have some summary, we just want to update it
    summary_data = {}
    if prev_summary_path:
        with open(os.path.join(prev_summary_path), "r") as f:
            summary_data = json.load(f)

    for folder in measurement_folders:
        h = dirhash(folder)
        if h not in hashes:
            sum_up(folder, summary_data)
            hashes.add(h)

    with open(os.path.join(output_path, "summary-data.json"), "w") as f:
        json.dump(summary_data, f, indent=4)

    with open(os.path.join(output_path, "hash-file"), "w") as f:
        json.dump(list(hashes), f, indent=4)


@click.command()
@click.argument("summary_path", type=click.Path(file_okay=True, dir_okay=False, readable=True))
@click.argument("export_type", type=click.Choice(["latex", "md", "fancy-md"]))
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    default=".",
)
def summary_export(summary_path, export_type, output_path):
    with open(summary_path, "r") as f:
        summary_data = json.load(f)

    df = pd.DataFrame(summary_data.values())
    df = df.sort_values(by=['TPM name'])

    if 'latex' in export_type:
        fmt = 'latex'
    elif 'md' in export_type:
        fmt = 'github'
    else:
        fmt = 'fancy_grid'

    print(df.to_markdown(index=False, tablefmt=fmt))





