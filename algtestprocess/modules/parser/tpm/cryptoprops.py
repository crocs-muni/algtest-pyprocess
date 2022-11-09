import pandas as pd
import re
import os


class CryptoProps:
    """
    Cryptographic properties parser
    Note: reads several CSV files
    """

    # Counter for devices of which device name was not available
    # Needs to be unique so class variable is useful
    unknown_devname_counter = 0

    def __init__(self, path: str):
        self.path = path
        self.device_name = self.get_device_name()

    def get_device_name(self):
        """Retrieves device name from neighbour folder"""
        files = [
            os.path.join(root, file)
            for root, _, files in os.walk(f"{self.path}/..")
            for file in files
        ]
        files = list(
            filter(
                lambda name: ".csv" in name
                and ("/performance/" in name.lower() or "/results/" in name.lower()),
                files,
            )
        )
        filenames = list(set(map(lambda name: re.sub(".*/", "", name), files)))
        if len(filenames) < 1:
            self.unknown_devname_counter += 1
            filename = f"Unknown TPM {self.unknown_devname_counter}"
        else:
            filename = filenames[0].replace(".csv", "").replace("_", " ")
        return filename

    def parse_legacy(self):
        return self.parse(legacy=True)

    def parse(self, legacy=False):
        items = [
            ("rsa_1024", "Keygen:RSA_1024.csv"),
            ("rsa_1024", "Keygen_RSA_1024.csv"),
            ("rsa_2048", "Keygen:RSA_2048.csv"),
            ("rsa_2048", "Keygen_RSA_2048.csv"),
            ("rsa_2048", "Keygen:RSA_2048.csv"),
            ("ecc_p192", "Keygen_ECC_0x0001.csv"),
            ("ecc_p224", "Keygen_ECC_0x0002.csv"),
            ("ecc_p256", "Keygen_ECC_0x0003.csv"),
            ("ecc_p384", "Keygen_ECC_0x0004.csv"),
            ("ecc_p521", "Keygen_ECC_0x0005.csv"),
            ("ecc_bn256", "Keygen_ECC_0x0010.csv"),
            ("ecc_bn638", "Keygen_ECC_0x0011.csv"),
            ("ecc_sm256", "Keygen_ECC_0x0020.csv"),
            ("ecc_p256_ecdsa", "Cryptoops_Sign:ECC_0x0003_0x0018.csv"),
            ("ecc_p256_ecdaa", "Cryptoops_Sign:ECC_0x0003_0x001a.csv"),
            ("ecc_p256_ecschnorr", "Cryptoops_Sign:ECC_0x0003_0x001c.csv"),
            ("ecc_p384_ecdsa", "Cryptoops_Sign:ECC_0x0004_0x0018.csv"),
            ("ecc_p384_ecdaa", "Cryptoops_Sign:ECC_0x0004_0x001a.csv"),
            ("ecc_p384_ecschnorr", "Cryptoops_Sign:ECC_0x0004_0x001c.csv"),
            ("ecc_bn256_ecdsa", "Cryptoops_Sign:ECC_0x0010_0x0018.csv"),
            ("ecc_bn256_ecdaa", "Cryptoops_Sign:ECC_0x0010_0x001a.csv"),
            ("ecc_bn256_ecschnorr", "Cryptoops_Sign:ECC_0x0010_0x001c.csv"),
        ]
        output = {}
        for key, filename in items:
            try:
                if output.get(key) is None:
                    path = f"{self.path}/{filename}"
                    output[key] = pd.read_csv(
                        path,
                        header=0,
                        # Legacy csv files had ; as delimiter
                        delimiter=";" if legacy else ",",
                    )
            except FileNotFoundError:
                continue
        if not output:
            return None

        output["device_name"] = self.device_name
        return output
