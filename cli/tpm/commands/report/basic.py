import gc
import json
import logging
import os.path
from functools import partial
from typing import Dict, List, Union

import click
import pandas as pd
from checksumdir import dirhash

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from algtestprocess.modules.visualization.heatmap import Heatmap
from cli.tpm.utils import _walk

ReportEntry = Dict[str, Union[str, List[str]]]
"""
{
    "TPM name": str,
    "vendor": str,
    "title": str,
    "measurement paths": List[str]
}
"""

Hashes = List[str]
ReportMetadata = Dict[str, Union[ReportEntry, Hashes]]
"""
ReportEntry = {
    "hashes" = List[str],
    "entries" = Dict[tpm_name||key, ReportEntry]
}
"""


def process_measurement_folders(metadata: ReportMetadata, measurement_folders,
                                key: str):
    if metadata.get("entries") is None:
        metadata["entries"] = {}

    # Load hashes of already included folders
    if metadata.get("hashes") is None:
        hashes = set()
    else:
        hashes = set(metadata["hashes"])

    for folder in measurement_folders:
        # First check if folder already isn't in hashes
        h = dirhash(folder)
        if h in hashes:
            logging.info(
                f"process_measurement_folders: {folder=} was already in hashes")
            continue

        hashes.add(h)

        # We try to parse each, so that in final report only successfully parse-able profiles are included
        try:
            manager = TPMProfileManager(folder)
            support = manager.support_profile

            tpm_name = None
            vendor = None
            if support is not None:
                tpm_name = support.device_name
                vendor = support.manufacturer

            if tpm_name is None:
                performance = manager.performance_profile
                if performance:
                    tpm_name = performance.device_name
                    vendor = performance.manufacturer

                if tpm_name is None:
                    logging.warning(
                        f"process_measurement_folders: unable to retrieve TPM name in {folder=}")
                    del manager
                    continue

            del manager
        except:
            logging.error(
                f"process_measurement_folders: {folder} unknown error, typically parsing old format")
            continue

        prefix = "" if key == "" else " "
        entry_key = f"{tpm_name}{prefix}{key}"
        entry = metadata["entries"].get(entry_key)

        if entry is None:
            entry = {
                "TPM name": tpm_name,
                "vendor": vendor,
                "title": key,
                "measurement paths": []
            }
        entry["measurement paths"].append(folder)

        metadata["entries"][entry_key] = entry

    metadata["hashes"] = list(hashes)


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
    "--prev-report-metadata-path",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    default=None
)
@click.option("--key", type=click.STRING, default="")
def report_update(measurements_path, output_path, prev_report_metadata_path,
                  key):
    """
    Over several steps collects metadata on what is to be included in the report,
    preventing things such as double includes and similar.
    """
    logging.info(
        f"report_update: "
        f"{measurements_path=}, "
        f"{output_path=}, "
        f"{prev_report_metadata_path=}, "
    )

    metadata: ReportMetadata = {}

    if prev_report_metadata_path is not None:
        try:
            with open(os.path.join(prev_report_metadata_path), "r") as f:
                metadata = json.load(f)
        except:
            logging.critical("report_update: opening metadata didn't work")

    if not metadata and prev_report_metadata_path is not None:
        logging.warning("report_update: metadata is empty")

    measurement_folders = _walk(measurements_path, 3)

    if not measurement_folders:
        logging.warning(
            f"report_update: no measurements folder found in {measurements_path=}")
        return

    process_measurement_folders(metadata, measurement_folders, key)

    with open(os.path.join(output_path, "report-metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)


def process_vendor(entries: List[ReportEntry], vendor: str, vendor_path: str):
    vendor_support_count = 0
    vendor_support_stats = {}
    for entry in entries:
        tpm_name = entry["TPM name"]
        title = entry["title"]
        performance = None
        support = None

        tpm_support_count = 0
        tpm_support_stats = {}

        tpm_dir = os.path.join(vendor_path, f"{tpm_name}{title}")
        os.mkdir(tpm_dir)

        # Prepare manager classes, and collect support statistics
        managers = []
        for measurement_path in entry["measurement paths"]:
            manager = TPMProfileManager(measurement_path)
            managers.append(manager)

            support_handle = manager.support_profile
            if support is None:
                support = support_handle

            if support_handle is not None:
                tpm_support_count += 1
                for result in support_handle.results.keys():
                    tpm_support_stats.setdefault(result, 0)
                    tpm_support_stats[result] += 1

            gc.collect()

        heatmap = lambda df: partial(
            Heatmap,
            rsa_df=df,
            device_name=tpm_name,
            title=title
        )

        # For each algorithm, create smaller dataframe which will fit in memory
        items = [
        (CryptoPropResultCategory.RSA_1024, ["n", "p", "q"], heatmap,"heatmap"),
            (CryptoPropResultCategory.RSA_2048, ["n", "p", "q"], heatmap,"heatmap"),
        ]

        for alg, cols, plot, pname in items:
            df = None
            for man in managers:
                cpps = man.cryptoprops

                if cpps is None:
                    logging.warning(f"process_vendor: manager for one of {tpm_name}{title} didn't find cryptoprops")
                    continue

                res = cpps.results.get(alg)

                if res is not None:
                    current_df = res.data
                    stripped_df = current_df.loc[:, cols]
                    if df is None:
                        df = stripped_df
                    else:
                        if len(df.index) >= 100000:
                            break
                        df = pd.concat([df, stripped_df])

            if df is None:
                logging.warning(f"process_vendor: {alg.value} for {tpm_name}{title} not found")
                continue

            if len(df.index) >= 5:
                plot(df)().build().save(os.path.join(tpm_dir, f"{pname}_{alg.value}.png"), format='png')
            gc.collect()

@click.command()
@click.argument("report_metadata_path",
                type=click.Path(exists=True, file_okay=True))
@click.option("--output-path", "-o",
              type=click.Path(exists=True, dir_okay=True), default=".")
def report_create(report_metadata_path, output_path):
    """
    Creates several folders and files, containing various info. Assumes we are
    content with all the folders we set up to be included in the report.

    Each path is relative to OUTPUT_PATH given as an argument

    ./tpm-report/report.{md/html}                                # Collected TPMs summary file
    ./tpm-report/VENDOR_NAME/vendor-report.{md/html}                    # Vendor summary file
    ./tpm-report/VENDOR_NAME/[TPM_NAME]/{*.png, report.{md/html} # TPM summary file and visualisations

    Vendor report layout

    # Vendor name

    | Support table with included percentages of supported commands |

    <Link or The table itself> The evolution of RSA generation in time

    Tpm report layout

    # Tpm name

    | Support table |

    Links to visualizations
    """
    try:
        metadata: ReportMetadata = {}
        with open(report_metadata_path, "r") as f:
            metadata = json.load(f)

        assert metadata
        entries = metadata["entries"].values()
        assert 0 < len(entries)
    except:
        logging.error("report_create: retrieving metadata was unsuccessful")
        return

    # We now group entries by vendor
    grouped = {}
    for entry in entries:
        vendor = entry.get("vendor")
        if vendor is None:
            logging.error(
                f"report_create: entry {entry} does not contain vendor")
            continue

        grouped.setdefault(vendor, [])
        grouped[vendor].append(entry)

    tpms_folder = os.path.join(output_path, "tpms")
    os.mkdir(tpms_folder)

    for vendor in grouped.keys():
        vendor_folder = os.path.join(tpms_folder, vendor)
        os.mkdir(vendor_folder)
        process_vendor(grouped[vendor], vendor, vendor_folder)
