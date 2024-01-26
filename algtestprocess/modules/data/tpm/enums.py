from enum import Enum


class CryptoPropResultCategory(Enum):
    RSA_1024 = "rsa_1024"
    RSA_2048 = "rsa_2048"
    RSA_3072 = "rsa_3072"
    RSA_1024_RSAPSS = "rsa_1024_rsapss"
    RSA_2048_RSAPSS = "rsa_2048_rsapss"
    RSA_1024_RSASSA = "rsa_1024_rsassa"
    RSA_2048_RSASSA = "rsa_2048_rsassa"
    ECC_P192 = "ecc_p192"
    ECC_P224 = "ecc_p224"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"
    ECC_P521 = "ecc_p521"
    ECC_BN256 = "ecc_bn256"
    ECC_BN638 = "ecc_bn638"
    ECC_SM256 = "ecc_sm256"
    ECC_P256_ECDSA = "ecc_p256_ecdsa"
    ECC_P256_ECDAA = "ecc_p256_ecdaa"
    ECC_P256_ECSCHNORR = "ecc_p256_ecschnorr"
    ECC_P384_ECDSA = "ecc_p384_ecdsa"
    ECC_P384_ECDAA = "ecc_p384_ecdaa"
    ECC_P384_ECSCHNORR = "ecc_p384_ecschnorr"
    ECC_BN256_ECDSA = "ecc_bn256_ecdsa"
    ECC_BN256_ECDAA = "ecc_bn256_ecdaa"
    ECC_BN256_ECSCHNORR = "ecc_bn256_ecschnorr"
    EK_RSA = "ek_rsa"
    EK_ECC = "ek_ecc"

    @classmethod
    def list(cls):
        return [x for x in CryptoPropResultCategory]
