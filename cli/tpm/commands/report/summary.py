import json
import logging
import os.path
from datetime import datetime
from typing import Dict, Union

import click

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager
from cli.tpm.commands.report.basic import ReportMetadata

Date = str
TPMName = str
MeasurementsStatistic = Dict[str, Union[str, int, Dict[Date, int]]]
"""
{
    "TPM name": str,
    "vendor": str,
    "firmware": str, 
    "count": str,
    "RSA EKs": int,
    "ECC EKs": int,
    "RSA Keys": int, 
    "ECC Signatures": int,
    "monthly additions": Dict[Date, int],
    "performance profiles": int,
    "support profiles": int,
    "cryptoprops profiles": int
}
"""


def measure(measurement_folder: str,
            stats: Dict[TPMName, MeasurementsStatistic]):
    try:
        man = TPMProfileManager(measurement_folder)
    except:
        logging.error(f"Could not load manager for {measurement_folder}")
        return

    cpps = man.cryptoprops
    support = man.support_profile
    performance = man.performance_profile

    # We need at least one type of profile
    valid = cpps or support or performance

    basic_info = False
    tpm_name = None
    vendor = None
    firmware = None
    for p, name in [(cpps, "cpps"), (support, "support"),
                    (performance, "performance")]:
        if p is None:
            logging.warning(
                f"Measurement at {measurement_folder=} has no {name} profile to be parsed")
        elif not basic_info:
            basic_info = True
            tpm_name = p.device_name
            vendor = p.manufacturer
            firmware = p.firmware_version

    if not valid:
        logging.error(
            f"Measurement at {measurement_folder=} has no profiles able to be parsed")
        return

    if not tpm_name or not vendor or not firmware:
        logging.error(
            f"Measurement at {measurement_folder=} has no basic info obtainable {tpm_name=}, {vendor=}, {firmware=}")
        return

    ek_rsa = 0
    ek_ecc = 0
    rsa_keys = 0
    ecdsa_signatures = 0
    if cpps:
        if cpps.results.get(CryptoPropResultCategory.EK_RSA):
            ek_rsa = 1

        if cpps.results.get(CryptoPropResultCategory.EK_ECC):
            ek_ecc = 1

        # For sake of simplicity, assume if RSA 2048 was successfully measured,
        # then also RSA 1024 would have same number of results
        rsa_result = cpps.results.get(CryptoPropResultCategory.RSA_2048)
        if rsa_result is not None:
            rsa_df = rsa_result.data
            if rsa_df is not None:
                rsa_keys = len(rsa_df.index)

        # Same as in the case of RSA, we assume if ECDSA was measured, then other
        # signature algorithms were measured
        ecdsa_result = cpps.results.get(CryptoPropResultCategory.ECC_P256_ECDSA)
        if ecdsa_result is not None:
            ecdsa_df = ecdsa_result.data
            if ecdsa_df is not None:
                ecdsa_signatures = len(ecdsa_df.index)

    date = None
    if support:
        date = datetime.strptime(
            support.test_info['Execution date/time'].replace('"', ''),
            '%Y/%m/%d %H:%M:%S'
        )
        date = date.strftime('%Y/%m') if date else None

    if stats.get(tpm_name):
        statistic = stats.get(tpm_name)
        statistic["count"] += 1
        statistic["RSA EKs"] += ek_rsa
        statistic["ECC EKs"] += ek_ecc
        statistic["RSA Keys"] += rsa_keys
        statistic["ECC Signatures"] += ecdsa_signatures
        if statistic["monthly additions"].get(date):
            statistic["monthly additions"][date] += 1
        else:
            statistic["monthly additions"][date] = 1
        statistic["performance profiles"] = 1 if performance else 0
        statistic["support profiles"] = 1 if support else 0
        statistic["cryptoprops profiles"] = 1 if cpps else 0

    else:
        statistic = {
            "TPM name": tpm_name,
            "vendor": vendor,
            "firmware": firmware,
            "count": 1,
            "RSA EKs": ek_rsa,
            "ECC EKs": ek_ecc,
            "RSA Keys": rsa_keys,
            "ECC Signatures": ecdsa_signatures,
            "monthly additions": {date: 1},
            "performance profiles": 1 if performance else 0,
            "support profiles": 1 if support else 0,
            "cryptoprops profiles": 1 if cpps else 0

        }
        stats[tpm_name] = statistic


@click.command()
@click.argument("report_metadata_path",
                type=click.Path(exists=True, file_okay=True))
@click.option("--output-path", "-o",
              type=click.Path(exists=True, dir_okay=True), default=".")
def summary_create(report_metadata_path, output_path):
    try:
        metadata: ReportMetadata = {}
        with open(report_metadata_path, "r") as f:
            metadata = json.load(f)

        assert metadata
        entries = metadata["entries"].values()
        assert 0 < len(entries)
    except:
        logging.error("summary_create: retrieving metadata was unsuccessful")
        return

    stats = {}
    for entry in entries:
        measurement_paths = entry.get("measurement paths")
        assert measurement_paths
        for folder in measurement_paths:
            measure(folder, stats)

    path = os.path.join(output_path, "measurement_stats.json")
    with open(path, "w") as f:
        json.dump({"data": list(stats.values())}, f, indent=2)
