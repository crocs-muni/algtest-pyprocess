import logging
import os
from typing import Optional

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.profiles.cryptoprops import CryptoProps
from algtestprocess.modules.data.tpm.results.cryptoprops import CryptoPropResult
from algtestprocess.modules.parser.tpm.utils import parse_ek


class CryptoPropsParser:
    """
    Cryptographic properties parser
    """

    def __init__(self, path: str):
        self.path = path
        assert os.path.exists(path) and os.path.isdir(path)

    def parse(self) -> Optional[CryptoProps]:
        items = [
            ("rsa_1024", "Keygen:RSA_1024.csv"),
            ("rsa_1024", "Keygen_RSA_1024.csv"),
            ("rsa_2048", "Keygen:RSA_2048.csv"),
            ("rsa_2048", "Keygen_RSA_2048.csv"),
            ("rsa_2048", "Keygen:RSA_2048.csv"),
            ("rsa_3072", "Keygen:RSA_3072.csv"),
            ("rsa_1024_rsassa", "Cryptoops_Sign:RSA_1024_0x0014.csv"),
            ("rsa_2048_rsassa", "Cryptoops_Sign:RSA_2048_0x0014.csv"),
            ("rsa_1024_rsapss", "Cryptoops_Sign:RSA_1024_0x0016.csv"),
            ("rsa_2048_rsapss", "Cryptoops_Sign:RSA_2048_0x0016.csv"),
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
        profile = CryptoProps(self.path)
        for key, filename in items:
            path = os.path.join(self.path, filename)
            if not os.path.exists(path) or not os.path.isfile(path):
                continue

            result = CryptoPropResult()
            result.category = CryptoPropResultCategory(key)
            result.paths.append(path)
            profile.add_result(result)

        eks = [
            ("ek_rsa", "Capability_ek-rsa.txt"),
            ("ek_rsa", "Certs_ek-rsa.txt"),
            ("ek_ecc", "Capability_ek-ecc.txt"),
            ("ek_ecc", "Certs_ek-ecc.txt"),
        ]

        for key, filename in eks:
            path = os.path.join(self.path, filename)
            if not os.path.exists(path) or not os.path.isfile(path):
                continue

            result = CryptoPropResult()
            result.category = CryptoPropResultCategory(key)
            result.paths.append(path)

            with open(path, "r") as f:
                result.data = [parse_ek(f.read())]
                if result.data is None:
                    logging.log(
                        logging.ERROR, f"Parsing of EK at {path=} was not successful"
                    )

            profile.add_result(result)

        if not profile.results:
            return None

        return profile
