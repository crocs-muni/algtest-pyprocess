from typing import Dict, Optional, Tuple, List
import click
import pandas as pd

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.manager import TPMProfileManager


ECCDataFrame = pd.DataFrame
DeviceName = str
FileName = str
PlotTitle = str


def process_profile(
    root_path: str, dupes: Optional[Dict[DeviceName, int]], algs: Optional[List[str]]
) -> Optional[
    List[Tuple[CryptoPropResultCategory, ECCDataFrame, DeviceName, FileName, PlotTitle]]
]:
    cpps = TPMProfileManager(root_path).cryptoprops

    if not cpps:
        return None

    algs_to_prepare = [
        ("ecc-p256-ecdsa", CryptoPropResultCategory.ECC_P256_ECDSA),
        ("ecc-p256-ecdaa", CryptoPropResultCategory.ECC_P256_ECDAA),
        ("ecc-p256_ecschnorr", CryptoPropResultCategory.ECC_P256_ECSCHNORR),
        ("ecc-p384-ecdsa", CryptoPropResultCategory.ECC_P384_ECDSA),
        ("ecc-p384-ecdaa", CryptoPropResultCategory.ECC_P384_ECDAA),
        ("ecc-p384-ecschnorr", CryptoPropResultCategory.ECC_P384_ECSCHNORR),
        ("ecc-bn256-ecdsa", CryptoPropResultCategory.ECC_BN256_ECDSA),
        ("ecc-bn256-ecdaa", CryptoPropResultCategory.ECC_BN256_ECDAA),
        ("ecc-bn256-ecschnorr", CryptoPropResultCategory.ECC_BN256_ECSCHNORR),
    ]
    items = []
    device_name = cpps.device_name
    for alg_id, alg_enum in algs_to_prepare:
        if algs is None or alg_id in algs:
            result = cpps.results.get(alg_enum)
            if not result:
                continue
            df = result.data
            df = df.loc[:, ["duration", "duration_extra", "nonce"]]
            idx = ""
            if dupes:
                assert dupes
                dupes.setdefault(device_name, 0)
                dupes[device_name] += 1
                idx = "_{0:03}".format(dupes[device_name])

            filename = f"spectrogram_{device_name.replace(' ', '-')}_{idx}_{alg_id}.png"

            title = alg_id.upper().replace("-", " ")
            items.append((alg_enum, df, device_name, filename, title))
    return items


@click.command()
@click.argument("root_path", type=click.Path(exists=True, dir_okay=True))
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
)
@click.option("--algs", type=click.Choice([], case_sensitive=False))
@click.option("--title", type=click.STRING, default="")
def spectrograms_single(root_path):
    """
    Creates spectrogram plots for single measurement

    ROOT_PATH is tpm2-algtest measurement folder root directory path,
    also known as the folder which has the following structure:

    \b
    . is the ROOT_PATH
    ./detail/ is REQUIRED folder
    ./performance.yaml
    ./results.yaml

    """
    # Somehow process the profile
    # then create spectrograms


@click.command()
@click.argument("measurements_path", type=click.Path(exists=True, dir_okay=True))
@click.argument(
    "group_by",
    required=True,
    nargs=1,
    type=click.Choice(["HOST", "TPM"], case_sensitive=True),
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
)
def spectrograms_grouped(measurements_path, group_by, output_path):
    """
    Creates spectrogram plots for multiple measurements grouped by either
    HOST computer, or TPM device id.

    MEASUREMENTS_FOLDER is a directory path containing tpm2-algtest
    measurement folders. There CANNOT be any intermediate folders.
    """
    pass
