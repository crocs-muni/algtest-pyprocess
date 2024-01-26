import json
import logging
import os.path
import os 
from datetime import datetime
from xml.etree import ElementTree as ET
import re
from typing import Dict

import click

from algtestprocess.modules.cli.tpm.types import (MeasurementsStatistic,
                                                  ReportMetadata, TPMName)
from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager


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
            tpm_name = f"{p.manufacturer} {p.firmware_version}"
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
    
    
    pt_year = support.results.get('TPM2_PT_YEAR').value
    pt_revision = support.results.get('TPM2_PT_REVISION').value
    pt_day_of_year = support.results.get('TPM2_PT_DAY_OF_YEAR').value

    image_tag = support.test_info['Image tag'].strip('" ')

    # Check if we have any ecc cryptoprops results
    ecc = False
    if cpps is not None:
        sig_algs = ['ecdsa', 'ecdaa', 'ecschnorr']
        supp_algs = {x for x in cpps.results.keys() if any([y in x.value for y in sig_algs])}
        ecc = supp_algs != set() and any(
            [res.data is not None and len(res.data.index) > 100  for alg in supp_algs if (res := cpps.results.get(alg)) is not None])

    def retrieve_result_count(category):
        out = 0
        result = cpps.results.get(category)
        if result is not None:
            df = result.data
            if df is not None:
                out = len(df.index)
        return out

    ek_ecc = 0
    ek_rsa = 0
    rsa3072_keys = 0
    rsa2048_keys = 0
    rsa1024_keys = 0

    ecdsa_p256_signatures = 0
    ecdaa_p256_signatures = 0
    ecschnorr_p256_signatures = 0    
    
    ecdsa_p384_signatures = 0
    ecdaa_p384_signatures = 0
    ecschnorr_p384_signatures = 0
    
    ecdsa_bn256_signatures = 0
    ecdaa_bn256_signatures = 0
    ecschnorr_bn256_signatures = 0

    rsapss_1024_signatures = 0
    rsapss_2048_signatures = 0

    rsassa_1024_signatures = 0
    rsassa_2048_signatures = 0

    ecc_p192  = 0
    ecc_p224  = 0
    ecc_p256  = 0
    ecc_p384  = 0
    ecc_p521  = 0
    ecc_bn256 = 0
    ecc_bn638 = 0
    ecc_sm256 = 0


    if cpps:
        if cpps.results.get(CryptoPropResultCategory.EK_RSA):
            ek_rsa = 1

        if cpps.results.get(CryptoPropResultCategory.EK_ECC):
            ek_ecc = 1

        rsa3072_keys = retrieve_result_count(CryptoPropResultCategory.RSA_3072)
        rsa2048_keys = retrieve_result_count(CryptoPropResultCategory.RSA_2048)
        rsa1024_keys = retrieve_result_count(CryptoPropResultCategory.RSA_1024)

        ecdsa_p256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P256_ECDSA)
        ecdaa_p256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P256_ECDAA)
        ecschnorr_p256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P256_ECSCHNORR)

        ecdsa_p384_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P384_ECDSA)
        ecdaa_p384_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P384_ECDAA)
        ecschnorr_p384_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_P384_ECSCHNORR)

        ecdsa_bn256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_BN256_ECDSA)
        ecdaa_bn256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_BN256_ECDAA)
        ecschnorr_bn256_signatures = retrieve_result_count(CryptoPropResultCategory.ECC_BN256_ECSCHNORR)


        rsapss_1024_signatures = retrieve_result_count(CryptoPropResultCategory.RSA_1024_RSAPSS)
        rsapss_2048_signatures = retrieve_result_count(CryptoPropResultCategory.RSA_2048_RSAPSS)


        rsassa_1024_signatures = retrieve_result_count(CryptoPropResultCategory.RSA_1024_RSASSA)
        rsassa_2048_signatures = retrieve_result_count(CryptoPropResultCategory.RSA_2048_RSASSA)

        ecc_p192 = retrieve_result_count(CryptoPropResultCategory.ECC_P192)
        ecc_p224 = retrieve_result_count(CryptoPropResultCategory.ECC_P224)
        ecc_p256 = retrieve_result_count(CryptoPropResultCategory.ECC_P256)
        ecc_p384 = retrieve_result_count(CryptoPropResultCategory.ECC_P384)
        ecc_p521 = retrieve_result_count(CryptoPropResultCategory.ECC_P521)
        ecc_bn256 = retrieve_result_count(CryptoPropResultCategory.ECC_BN256)
        ecc_bn638 = retrieve_result_count(CryptoPropResultCategory.ECC_BN638)
        ecc_sm256 = retrieve_result_count(CryptoPropResultCategory.ECC_SM256)



    convert_to_int = lambda x: int(x, 16) if isinstance(x, str) else x

    if stats.get(tpm_name):
        statistic = stats.get(tpm_name)
        statistic["tpm2-algtest"] = True
        statistic["tpm version"] = "2.0"

        statistic.setdefault("tpm2-algtest measurement count", 0)
        statistic["tpm2-algtest measurement count"] += 1

        statistic.setdefault("rsa eks", 0)
        statistic["rsa eks"] += ek_rsa

        statistic.setdefault("ecc eks", 0)
        statistic["ecc eks"] += ek_ecc

        statistic.setdefault("rsa 1024 keys", 0)
        statistic["rsa 1024 keys"] += rsa1024_keys

        statistic.setdefault("rsa 2048 keys", 0)
        statistic["rsa 2048 keys"] += rsa2048_keys

        statistic.setdefault("rsa 3072 keys", 0)
        statistic["rsa 3072 keys"] += rsa3072_keys

        statistic.setdefault("ecdsa p256 signatures", 0)
        statistic["ecdsa p256 signatures"] += ecdsa_p256_signatures

        statistic.setdefault("ecdaa p256 signatures", 0)
        statistic["ecdaa p256 signatures"] += ecdaa_p256_signatures

        statistic.setdefault("ecschnorr p256 signatures", 0)
        statistic["ecschnorr p256 signatures"] += ecschnorr_p256_signatures

        statistic.setdefault("ecdsa p384 signatures", 0)
        statistic["ecdsa p384 signatures"] += ecdsa_p384_signatures

        statistic.setdefault("ecdaa p384 signatures", 0)
        statistic["ecdaa p384 signatures"] += ecdaa_p384_signatures

        statistic.setdefault("ecschnorr p384 signatures", 0)
        statistic["ecschnorr p384 signatures"] += ecschnorr_p384_signatures

        statistic.setdefault("ecdsa bn256 signatures", 0)
        statistic["ecdsa bn256 signatures"] += ecdsa_bn256_signatures

        statistic.setdefault("ecdaa bn256 signatures", 0)
        statistic["ecdaa bn256 signatures"] += ecdaa_bn256_signatures

        statistic.setdefault("ecschnorr bn256 signatures", 0)
        statistic["ecschnorr bn256 signatures"] += ecschnorr_bn256_signatures

        statistic.setdefault("rsapss 1024 signatures", 0)
        statistic["rsapss 1024 signatures"] += rsapss_1024_signatures

        statistic.setdefault("rsapss 2048 signatures", 0)
        statistic["rsapss 2048 signatures"] += rsapss_2048_signatures

        statistic.setdefault("rsassa 1024 signatures", 0)
        statistic["rsassa 1024 signatures"] += rsassa_1024_signatures

        statistic.setdefault("rsassa 2048 signatures", 0)
        statistic["rsassa 2048 signatures"] += rsassa_2048_signatures

        statistic.setdefault("performance profiles", 0)
        statistic["performance profiles"] += 1 if performance else 0

        statistic.setdefault("support profiles", 0)
        statistic["support profiles"] += 1 if support else 0

        statistic.setdefault("cryptoprops profiles", 0)
        statistic["cryptoprops profiles"] += 1 if cpps else 0

        statistic.setdefault("ecc p192 keys", 0)
        statistic["ecc p192 keys"] += ecc_p192

        statistic.setdefault("ecc p224 keys", 0)
        statistic["ecc p224 keys"] += ecc_p224

        statistic.setdefault("ecc p256 keys", 0)
        statistic["ecc p256 keys"] += ecc_p256

        statistic.setdefault("ecc p384 keys", 0)
        statistic["ecc p384 keys"] += ecc_p384

        statistic.setdefault("ecc p521 keys", 0)
        statistic["ecc p521 keys"] += ecc_p521

        statistic.setdefault("ecc bn256 keys", 0)
        statistic["ecc bn256 keys"] += ecc_bn256

        statistic.setdefault("ecc bn638 keys", 0)
        statistic["ecc bn638 keys"] += ecc_bn638

        statistic.setdefault("ecc sm256 keys", 0)
        statistic["ecc sm256 keys"] += ecc_sm256

        statistic['year'] = convert_to_int(pt_year)
        statistic['day'] = convert_to_int(pt_day_of_year)
        statistic['tpm revision'] = pt_revision

        statistic.setdefault('image tag', [])
        if image_tag not in statistic['image tag']:
            statistic['image tag'].append(image_tag)

        statistic.setdefault('ecc', False)
        statistic['ecc'] |= ecc 

    else:
        statistic = {
            "tpm name": tpm_name,
            "tpm2-algtest": True,
            "tpm version": "2.0",
            "tpm_pcr": False,
            "tpm2-algtest measurement count": 1,
            "rsa eks": ek_rsa,
            "ecc eks": ek_ecc,
            "rsa 1024 keys": rsa1024_keys,
            "rsa 2048 keys": rsa2048_keys,
            "rsa 3072 keys": rsa3072_keys,

            "ecdsa p256 signatures" : ecdsa_p256_signatures,
            "ecdaa p256 signatures" : ecdaa_p256_signatures,
            "ecschnorr p256 signatures" : ecschnorr_p256_signatures,
            "ecdsa p384 signatures" :ecdsa_p384_signatures,
            "ecdaa p384 signatures" : ecdaa_p384_signatures,
            "ecschnorr p384 signatures" : ecschnorr_p384_signatures,
            "ecdsa bn256 signatures" : ecdsa_bn256_signatures,
            "ecdaa bn256 signatures" : ecdaa_bn256_signatures,
            "ecschnorr bn256 signatures" : ecschnorr_bn256_signatures,
            "rsapss 1024 signatures" : rsapss_1024_signatures,
            "rsapss 2048 signatures" : rsapss_2048_signatures,
            "rsassa 1024 signatures": rsassa_1024_signatures,
            "rsassa 2048 signatures": rsassa_2048_signatures,

            "ecc p192 keys": ecc_p192,  
            "ecc p224 keys": ecc_p224,
            "ecc p256 keys": ecc_p256,
            "ecc p384 keys": ecc_p384,
            "ecc p521 keys": ecc_p521,
            "ecc bn256 keys": ecc_bn256,
            "ecc bn638 keys": ecc_bn638,
            "ecc sm256 keys": ecc_sm256,

            "performance profiles": 1 if performance else 0,
            "support profiles": 1 if support else 0,
            "cryptoprops profiles": 1 if cpps else 0, 

            "year": convert_to_int(pt_year),
            "day" : convert_to_int(pt_day_of_year), 
            "tpm revision": pt_revision,
            "image tag": [image_tag],
            "ecc": ecc

        }
        stats[tpm_name] = statistic

errors = {
    "145.1.0.0": "401.1.0.0",
    "146.1.0.0": "402.1.0.0",
    "147.1.0.0": "403.1.0.0",
    "46.12.0.0": "302.12.0.0",
    "5.1058": "11.5.0.1058",
    "6.1121": "11.6.0.1121",
    "7.3290": "11.7.0.3290"
}

def walk(current_dir, depth, predicate=None):
    """
    Tries to find all the paths for measurement folders

    Sentinel of the recursion is finding a txt file 

    :param current_dir: the directory we process now
    :return: list of paths to valid measurement folders
    """
    if predicate is None:
        predicate = lambda x: x.is_file() and '.txt' in x.name

    scan = list(os.scandir(current_dir))

    if any([predicate(entry) for entry in scan]):
        return [current_dir]

    if depth <= 0:
        return []

    result = []
    for entry in scan:
        if entry.is_dir():
            result += walk(entry.path, depth - 1)

    return result

def measure_tpm_pcr(tpm_pcr_path, stats, output_path):
    measurements = {}
    for path in walk(tpm_pcr_path, 10):
        scan = list(os.scandir(path))
        for entry in scan:
            try:
                tree = ET.parse(entry.path)
            except Exception: # Actually throws ParseError
                continue
            
            # Get root and retrieve EK
            root = tree.getroot() 
            ek = root.find('EK')

            # If there is no EK, we continue
            if ek is None:
                continue
            ek = ek.text

            # If there is EK, we assume there is RSK
            rsk = root.find('RSK')
            assert rsk is not None
            rsk = rsk.text

            # And there MUST be firmware version
            fw = root.findall('.//FirmwareVersion')
            if fw == []:
                print(entry.path)
                continue
            fw = fw[0].text
            fw = fw.replace('  ', ' ')

            if 'INTC' in fw:
                for err in errors:
                    if err in fw:
                        fw = fw.replace(err, errors[err])
                        break

            tpm = root.findall('.//TPM')
            tpm_version = None
            tpm_revision = None
            
            if tpm == []:
                print(f"No <TPM> tag found {entry.path}")
            else:
                if (res := re.search(r"TPM-Version:(\d+\.\d+).*Revision:(\d+\.\d+)", tpm[0].text)) is not None:
                    tpm_version = res.group(1)
                    tpm_revision = res.group(2)
                
            stats.setdefault(fw, {'tpm name': fw, 'tpm version': tpm_version, 'tpm revision': tpm_revision, 'tpm_pcr': True, 'tpm2-algtest': False})

            measurements.setdefault(fw, {'TPM Version': tpm_version, 'TPM Revision': tpm_revision,'EK':[], 'RSK': [], 'paths': []})

            
            if ek not in measurements[fw]['EK'] or rsk not in measurements[fw]['RSK']:
                measurements[fw]['EK'].append(ek)
                measurements[fw]['RSK'].append(rsk)
                measurements[fw]['paths'].append(entry.path)
                stats[fw].setdefault('rsa eks', 0)
                stats[fw].setdefault('rsa rsks', 0)
                stats[fw]['rsa eks'] += 1
                stats[fw]['rsa rsks'] += 1

    with open(os.path.join(output_path, 'tpm-pcr-metadata.json'), 'w') as f:
        json.dump(measurements, f, indent=4)


@click.command()
@click.argument("report_metadata_path",
                type=click.Path(exists=True, file_okay=True))
@click.option("--tpm-pcr-path", type=click.Path(exists=True, dir_okay=True), default=None)
@click.option("--output-path", "-o",
              type=click.Path(exists=True, dir_okay=True), default=".")
def summary_create(report_metadata_path, tpm_pcr_path, output_path):
    # Open metadata.json
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

    # Create stats
    stats = {}

    # Parse info from TPM-PCR measurements
    if tpm_pcr_path is not None:
        measure_tpm_pcr(tpm_pcr_path, stats, output_path)

    # Parse info from tpm2-algtest measurements
    for entry in entries:
        measurement_paths = entry.get("measurement paths")
        assert measurement_paths
        for folder in measurement_paths:
            measure(folder, stats)


    with open(os.path.join(output_path, "measurement_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)