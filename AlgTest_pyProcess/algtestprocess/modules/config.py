class TopFunctions:
    SYM = [
        ("SECURE RANDOM (256B)", "ALG_SECURE_RANDOM RandomData_generateData()"),
        ("SHA-1 hash (256B)", "ALG_SHA MessageDigest_doFinal()"),
        ("SHA2-256 hash (256B)", "ALG_SHA_256 MessageDigest_doFinal()"),
        ("AES128 encrypt (256B)", "TYPE_AES LENGTH_AES_128 ALG_AES_BLOCK_128_CBC_NOPAD Cipher_doFinal()"),
        ("AES256 encrypt (256B)", "TYPE_AES LENGTH_AES_256 ALG_AES_BLOCK_128_CBC_NOPAD Cipher_doFinal()"),
        ("3DES encrypt (256B)", "TYPE_DES LENGTH_DES3_3KEY ALG_DES_CBC_NOPAD Cipher_doFinal()"),
        ("3DES setKey(192b)", "TYPE_DES LENGTH_DES_192 setKey()"),
        ("AES setKey(128b)", "TYPE_AES LENGTH_AES_128 setKey()"),
        ("AES setKey(256b)", "TYPE_AES LENGTH_AES_256 setKey()"),
        ("SWAES oneblock (16B)", "SWALGS SWAlgs_AES()"),
        ("arrayCopy nonAtomic RAM2RAM (256B)", "UTIL Util_arrayCopyNonAtomic_RAM()"),
        ("arrayCopy nonAtomic EEPROM2EEPROM (256B)", "UTIL Util_arrayCopyNonAtomic_EEPROM()")
     ]

    ASYM = [
        ("ECC 256b genKeyPair", "ALG_EC_FP LENGTH_EC_FP_256 KeyPair_genKeyPair()"),
        ("ECDSA 256b sign", "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_sign()"),
        ("ECDSA 256b verify", "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_verify()"),
        ("ECDH 256b", "ALG_EC_FP LENGTH_EC_FP_256 ALG_EC_SVDP_DH KeyAgreement_generateSecret()"),
        ("RSA2048 CRT decrypt", "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 CRT encrypt", "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 CRT generate", "ALG_RSA_CRT LENGTH_RSA_2048 KeyPair_genKeyPair()"),
        ("RSA2048 decrypt", "TYPE_RSA_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 encrypt", "TYPE_RSA_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 generate", "ALG_RSA LENGTH_RSA_2048 KeyPair_genKeyPair()"),
        ("RSA1024 CRT generate", "ALG_RSA_CRT LENGTH_RSA_1024 KeyPair_genKeyPair()"),
        ("RSA1024 CRT decrypt", "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 CRT encrypt", "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 generate", "ALG_RSA LENGTH_RSA_1024 KeyPair_genKeyPair()"),
        ("RSA1024 decrypt", "TYPE_RSA_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 encrypt", "TYPE_RSA_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()")
    ]

    ALL = list(map(lambda x: x[1], SYM + ASYM))


class SimilarityFunctions:
    RSA = [
        "TYPE_RSA_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"
    ]

    RSA_CRT = [
        "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()",
        "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"
    ]

    ECC = [
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_192 Signature_ALG_ECDSA_SHA Signature_sign()",
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_192 Signature_ALG_ECDSA_SHA Signature_verify()",
        "ALG_EC_FP LENGTH_EC_FP_192 ALG_EC_SVDP_DH KeyAgreement_init()",
        "ALG_EC_FP LENGTH_EC_FP_192 ALG_EC_SVDP_DH KeyAgreement_generateSecret()",
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_sign()",
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_verify()",
        "ALG_EC_FP LENGTH_EC_FP_256 ALG_EC_SVDP_DH KeyAgreement_init()",
        "ALG_EC_FP LENGTH_EC_FP_256 ALG_EC_SVDP_DH KeyAgreement_generateSecret()",
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_384 Signature_ALG_ECDSA_SHA Signature_sign()",
        "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_384 Signature_ALG_ECDSA_SHA Signature_verify()",
        "ALG_EC_FP LENGTH_EC_FP_384 ALG_EC_SVDP_DH KeyAgreement_init()",
        "ALG_EC_FP LENGTH_EC_FP_384 ALG_EC_SVDP_DH KeyAgreement_generateSecret()"
    ]

    ENC = [
        "TYPE_DES LENGTH_DES ALG_DES_ECB_NOPAD Cipher_doFinal()",
        "TYPE_DES LENGTH_DES3_2KEY ALG_DES_ECB_NOPAD Cipher_doFinal()",
        "ALG_SECURE_RANDOM RandomData_generateData()",
        "TYPE_AES LENGTH_AES_128 ALG_AES_BLOCK_128_ECB_NOPAD Cipher_doFinal()",
        "TYPE_AES LENGTH_AES_128 ALG_AES_BLOCK_256_ECB_NOPAD Cipher_doFinal()",
        "TYPE_AES LENGTH_AES_128 setKey()",
        "TYPE_AES LENGTH_AES_256 setKey()"
    ]

    HASH = [
        "ALG_SHA MessageDigest_doFinal()",
        "ALG_SHA_256 MessageDigest_doFinal()",
        "ALG_SHA_512 MessageDigest_doFinal()"
    ]

    SW = [
        "SWALGS SWAlgs_AES()",
        "SWALGS SWAlgs_xor()"
    ]

    ALL = RSA + RSA_CRT + ECC + ENC + HASH + SW

    GROUPS = [RSA, RSA_CRT, ECC, ENC, HASH, SW]


class SupportGroups:

    ECC_ALGS = [
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_112",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_128",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_160",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_192",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_224",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_256",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_384",
        "TYPE_EC_FP_PRIVATE LENGTH_EC_FP_521"
    ]
    RSA2048BIGGER_ALGS = [
        "TYPE_RSA_PUBLIC LENGTH_RSA_3072",
        "TYPE_RSA_PRIVATE LENGTH_RSA_3072",
        "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_3072",
        "TYPE_RSA_PUBLIC LENGTH_RSA_4096",
        "TYPE_RSA_PRIVATE LENGTH_RSA_4096",
        "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_4096"
    ]
    ECDH_ALGS = [
        "ALG_EC_SVDP_DH/ALG_EC_SVDP_DH_KDF",
        "ALG_EC_SVDP_DHC/ALG_EC_SVDP_DHC_KDF",
        "ALG_EC_SVDP_DH_PLAIN",
        "ALG_EC_SVDP_DHC_PLAIN",
        "ALG_EC_PACE_GM",
        "ALG_EC_SVDP_DH_PLAIN_XY",
        "ALG_DH_PLAIN"
    ]
    AES_ALGS = [
        "TYPE_AES LENGTH_AES_128",
        "TYPE_AES LENGTH_AES_192",
        "TYPE_AES LENGTH_AES_256"
    ]
    SHA2_ALGS = [
        "ALG_SHA_256",
        "ALG_SHA_384",
        "ALG_SHA_512",
        "ALG_SHA_224"
    ]
    SHA2_512_ALGS = [
        "ALG_SHA_512"
    ]
    SHA3_ALGS = [
        "ALG_SHA3_224",
        "ALG_SHA3_256",
        "ALG_SHA3_384",
        "ALG_SHA3_512"
    ]
    DH_PLAIN_ALGS = [
        "ALG_EC_SVDP_DH_PLAIN_XY",
        "ALG_EC_SVDP_DHC_PLAIN",
        "ALG_EC_SVDP_DH_PLAIN",
        "ALG_DH_PLAIN"
    ]
    ECDSA_SHA256_ALGS = [
        "ALG_ECDSA_SHA_256"
    ]

    GROUPS = [
        ("ECC", ECC_ALGS),
        ("large RSA", RSA2048BIGGER_ALGS),
        ("ECDH", ECDH_ALGS),
        ("AES", AES_ALGS),
        ("SHA2", SHA2_ALGS),
        ("SHA2_512b", SHA2_512_ALGS),
        ("SHA3", SHA3_ALGS),
        ("plain ECDH", DH_PLAIN_ALGS),
        ("ECDSA", ECDSA_SHA256_ALGS)
    ]
