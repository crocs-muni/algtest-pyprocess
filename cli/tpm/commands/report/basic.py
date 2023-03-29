import json
import logging
import os.path
from typing import Dict

import click
from checksumdir import dirhash

from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from cli.tpm.utils import _walk

ReportEntry = Dict[str, any]
"""
{
    "TPM name": str
    "title": str,
    "measurement paths": List[str]
}
"""

ReportMetadata = Dict[str, any]
"""
ReportEntry = {
    "hashes" = Set[str],
    "entries" = Dict[tpm_name||key, ReportEntry]
}
"""


def process_measurement_folders(metadata: ReportMetadata, measurement_folders, key: str):
    if metadata.get("entries") is None:
        metadata["entries"] = {}

    # Load hashes of already included folders
    if metadata.get("hashes") is None:
        hashes = set()
    else:
        hashes = set(metadata["hashes"])

    for folder in measurement_folders:
        # First check if folder already isnt in hashes
        h = dirhash(folder)
        if h in hashes:
            logging.info(f"process_measurement_folders: {folder=} was already in hashes")
            continue

        hashes.add(h)

        # We try to parse each, so that in final report only sucessfully parse-
        # able profiles are included
        manager = TPMProfileManager(folder)
        support = manager.support_profile
        tpm_name = None
        if support is not None:
            tpm_name = support.device_name

        if tpm_name is None:
            performance = manager.performance_profile
            if performance:
                tpm_name = performance.device_name

            if tpm_name is None:
                logging.warning(f"process_measurement_folders: unable to retrieve TPM name in {folder=}")
                del manager
                continue
        del manager

        prefix = "" if key == "" else " "
        entry_key = f"{tpm_name}{prefix}{key}"
        entry = metadata["entries"].get(entry_key)

        if entry is None:
            entry = {
                "TPM name": tpm_name,
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
            logging.critical("report_update: opening metadata didnt work")

    if not metadata and prev_report_metadata_path is not None:
        logging.warning("report_update: metadata is empty")

    measurement_folders = _walk(measurements_path, 3)

    if not measurement_folders:
        logging.warning(f"report_update: no measurements folder found in {measurements_path=}")
        return

    process_measurement_folders(metadata, measurement_folders, key)

    with open(os.path.join(output_path, "report-metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

@click.command()
def report_create():
    """
    Creates several folders and files, containing various info. Assumes we are
    content with all the folders we set up to be included in the report.

    Each path is relative to OUTPUT_PATH given as an argument

    ./tpms/report.{md/html}                                # Collected TPMs summary file
    ./tpms/VENDOR_NAME/report.{md/html}                    # Vendor summary file
    ./tpms/VENDOR_NAME/[TPM_NAME]/{*.png, report.{md/html} # TPM summary file and visualisations
    """
    pass
