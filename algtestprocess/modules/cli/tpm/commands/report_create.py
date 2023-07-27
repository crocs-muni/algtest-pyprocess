import gc
import json
import logging
import os
import os.path
from functools import partial
from typing import List

import click
import pandas as pd

from algtestprocess.modules.cli.tpm.types import ReportEntry, ReportMetadata
from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from algtestprocess.modules.visualization.heatmap import Heatmap
from algtestprocess.modules.visualization.spectrogram import Spectrogram


def process_vendor(entries: List[ReportEntry], vendor: str, vendor_path: str):
    vendor_tpm_count = 0
    vendor_support_stats = {}
    for entry in entries:
        tpm_name = entry["TPM name"]
        title = entry["title"]
        support_found = False

        # Assuming that all TPMs with exact same firmware version and manufacturer support same capabilities
        # Because I have no idea to tell if the tpm2-algtest was just unsuccessful retrieving them, crashed,
        # or same TPMs really can have different capabilities
        tpm_support_stats = set()

        tpm_dir = os.path.join(vendor_path, f"{tpm_name}{title}")
        os.mkdir(tpm_dir)

        # Prepare manager classes, and collect support statistics
        managers = []
        for measurement_path in entry["measurement paths"]:
            manager = TPMProfileManager(measurement_path)
            managers.append(manager)

            support_handle = manager.support_profile

            if support_handle is not None and len(support_handle.results) > 0:
                support_found = True
                for capability in support_handle.results.keys():
                    tpm_support_stats.add(capability)
            gc.collect()

        if support_found:
            for capability in tpm_support_stats:
                if vendor_support_stats.get(capability) is None:
                    vendor_support_stats.setdefault(capability, 0)
                vendor_support_stats[capability] += 1
            vendor_tpm_count += 1

        # The plotting section
        heatmap = lambda df: partial(
            Heatmap,
            rsa_df=df,
            device_name=tpm_name,
            title=title
        )
        
        spectrogram = lambda df: partial(
            Spectrogram,
            df=df,
            device_name=tpm_name
        )

        # For each algorithm, create smaller dataframe which will fit in memory
        items = [
            (CryptoPropResultCategory.RSA_1024, ["n", "p", "q"], heatmap,
             "heatmap"),
            (CryptoPropResultCategory.RSA_2048, ["n", "p", "q"], heatmap,
             "heatmap"),
            (CryptoPropResultCategory.ECC_BN256_ECDSA, ["duration", "duration_extra","nonce"], spectrogram, "spectrogam"),
            (CryptoPropResultCategory.ECC_P256_ECDSA, ["duration", "duration_extra","nonce"], spectrogram, "spectrogam"),
            (CryptoPropResultCategory.ECC_P384_ECDSA, ["duration", "duration_extra","nonce"], spectrogram, "spectrogam"),
        ]

        for alg, cols, plot, pname in items:
            df = None
            for man in managers:
                cpps = man.cryptoprops

                if cpps is None:
                    logging.warning(
                        f"process_vendor: manager for one of {tpm_name}{title} didn't find cryptoprops")
                    continue

                res = cpps.results.get(alg)

                if res is not None:
                    current_df = res.data
                    
                    # If the dataframe does not contain nonce, then we will skip
                    # Some nonces, can be computed back from their coordinates on EC
                    # but for now those wont be recovered
                    if not set(cols).issubset(current_df.columns):
                        continue
                    
                    stripped_df = current_df.loc[:, cols]
                    if df is None:
                        df = stripped_df
                    else:
                        if len(df.index) >= 100000:
                            break
                        df = pd.concat([df, stripped_df])

            if df is None:
                logging.warning(
                    f"process_vendor: {alg.value} for {tpm_name}{title} not found")
                continue

            if len(df.index) >= 5:
                try:
                    plot(df)().build().save(
                    os.path.join(tpm_dir, f"{pname}_{alg.value}.png"),
                    format='png')
                except ValueError:
                    logging.error(f"Heatmap: RSA dataframe has {len(df)} for {tpm_name} has no rows")

            gc.collect()

    return vendor_tpm_count, vendor_support_stats


def _table(l: List[List[any]], cols, header):
    # header repeat col times
    out = ""
    out += "| " + (" | ".join(header) + " | ") * cols + "\n"
    out += "| " + ("|".join(["---"] * (cols * len(header))) + " | ") + "\n"

    i = 0
    while i < len(l):
        out += "| "
        for _ in range(cols):
            if i < len(l):
                entries = l[i]
            else:
                entries = [" " for _ in range(len(header))]

            assert len(entries) == len(header)

            out += " | ".join(map(str, entries)) + " | "
            i += 1
        out += "\n"
    return out


def make_support_table(stats, count, title, output_path):
    stats = [[alg] + [value, round(100 * (value / count), 2)] for
             alg, value in sorted(stats.items(), key=lambda x: x[0])]
    with open(os.path.join(output_path, "support.md"), "w") as f:
        f.write(f"# {title}\n")
        f.write(_table(stats, 1, ["Algorithm", "Support", "%"]))


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
    grouped = load_metadata(report_metadata_path)
    
    if grouped == {}:
        return

    # Create the tpms folder
    tpms_folder = os.path.join(output_path, "tpms")
    os.mkdir(tpms_folder)

    total_count, total_stats = 0, {}
    for vendor in grouped.keys():
        vendor_folder = os.path.join(tpms_folder, vendor)
        os.mkdir(vendor_folder)
        vendor_tpm_count, vendor_stats = process_vendor(grouped[vendor], vendor,
                                                        vendor_folder)

        if vendor_tpm_count > 0:
            total_count += vendor_tpm_count
            for capability, count in vendor_stats.items():
                if total_stats.get(capability) is None:
                    total_stats.setdefault(capability, 0)
                total_stats[capability] += count
            # Vendor support table
            make_support_table(vendor_stats, vendor_tpm_count, vendor,
                               vendor_folder)

    make_support_table(total_stats, total_count, 'Total support', tpms_folder)

def load_metadata(metadata_path):
    try:
        metadata: ReportMetadata = {}
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        assert metadata
        entries = metadata["entries"].values()
        assert 0 < len(entries)
    except:
        logging.error("report_create: retrieving metadata was unsuccessful")
        return {}

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
    return grouped