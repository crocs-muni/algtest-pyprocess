class TopFunctionsJC:
    """JavaCard Top Functions with abbreviations"""
    SYM = [
        ("SECURE RANDOM (256B)", "ALG_SECURE_RANDOM RandomData_generateData()"),
        ("SHA-1 hash (256B)", "ALG_SHA MessageDigest_doFinal()"),
        ("SHA2-256 hash (256B)", "ALG_SHA_256 MessageDigest_doFinal()"),
        ("AES128 encrypt (256B)",
         "TYPE_AES LENGTH_AES_128 ALG_AES_BLOCK_128_CBC_NOPAD Cipher_doFinal()"),
        ("AES256 encrypt (256B)",
         "TYPE_AES LENGTH_AES_256 ALG_AES_BLOCK_128_CBC_NOPAD Cipher_doFinal()"),
        ("3DES encrypt (256B)",
         "TYPE_DES LENGTH_DES3_3KEY ALG_DES_CBC_NOPAD Cipher_doFinal()"),
        ("3DES setKey(192b)", "TYPE_DES LENGTH_DES_192 setKey()"),
        ("AES setKey(128b)", "TYPE_AES LENGTH_AES_128 setKey()"),
        ("AES setKey(256b)", "TYPE_AES LENGTH_AES_256 setKey()"),
        ("SWAES oneblock (16B)", "SWALGS SWAlgs_AES()"),
        ("arrayCopy nonAtomic RAM2RAM (256B)",
         "UTIL Util_arrayCopyNonAtomic_RAM()"),
        ("arrayCopy nonAtomic EEPROM2EEPROM (256B)",
         "UTIL Util_arrayCopyNonAtomic_EEPROM()")
    ]

    ASYM = [
        ("ECC 256b genKeyPair",
         "ALG_EC_FP LENGTH_EC_FP_256 KeyPair_genKeyPair()"),
        ("ECDSA 256b sign",
         "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_sign()"),
        ("ECDSA 256b verify",
         "KeyPair_ALG_EC_FP KeyBuilder_LENGTH_EC_FP_256 Signature_ALG_ECDSA_SHA Signature_verify()"),
        ("ECDH 256b",
         "ALG_EC_FP LENGTH_EC_FP_256 ALG_EC_SVDP_DH KeyAgreement_generateSecret()"),
        ("RSA2048 CRT decrypt",
         "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 CRT encrypt",
         "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 CRT generate",
         "ALG_RSA_CRT LENGTH_RSA_2048 KeyPair_genKeyPair()"),
        ("RSA2048 decrypt",
         "TYPE_RSA_PRIVATE LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 encrypt",
         "TYPE_RSA_PUBLIC LENGTH_RSA_2048 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA2048 generate", "ALG_RSA LENGTH_RSA_2048 KeyPair_genKeyPair()"),
        ("RSA1024 CRT generate",
         "ALG_RSA_CRT LENGTH_RSA_1024 KeyPair_genKeyPair()"),
        ("RSA1024 CRT decrypt",
         "TYPE_RSA_CRT_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 CRT encrypt",
         "TYPE_RSA_CRT_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 generate", "ALG_RSA LENGTH_RSA_1024 KeyPair_genKeyPair()"),
        ("RSA1024 decrypt",
         "TYPE_RSA_PRIVATE LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()"),
        ("RSA1024 encrypt",
         "TYPE_RSA_PUBLIC LENGTH_RSA_1024 ALG_RSA_NOPAD Cipher_doFinal()")
    ]

    ALL = list(map(lambda x: x[1], SYM + ASYM))


class SimilarityFunctionsJC:
    """Groups for algorithm identifiers used in similarity table for JavaCards"""
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

    ABBREVIATIONS = ["RSA", "RSA_CRT", "ECC", "ENC", "HASH", "SW"]


class SimilarityFunctionsTPM:
    """Groups for algorithm identifiers used in similarity table for TPMs"""
    RSA_ENC_DEC = [
        'TPM2_RSA_Decrypt RSA 1024 TPM2_ALG_NULL',
        'TPM2_RSA_Decrypt RSA 1024 TPM2_ALG_OAEP',
        'TPM2_RSA_Decrypt RSA 1024 TPM2_ALG_RSAES',
        'TPM2_RSA_Decrypt RSA 2048 TPM2_ALG_NULL',
        'TPM2_RSA_Decrypt RSA 2048 TPM2_ALG_OAEP',
        'TPM2_RSA_Decrypt RSA 2048 TPM2_ALG_RSAES',
        'TPM2_RSA_Encrypt RSA 1024 TPM2_ALG_NULL',
        'TPM2_RSA_Encrypt RSA 1024 TPM2_ALG_OAEP',
        'TPM2_RSA_Encrypt RSA 1024 TPM2_ALG_RSAES',
        'TPM2_RSA_Encrypt RSA 2048 TPM2_ALG_NULL',
        'TPM2_RSA_Encrypt RSA 2048 TPM2_ALG_OAEP',
        'TPM2_RSA_Encrypt RSA 2048 TPM2_ALG_RSAES',
    ]

    RSA_SIGN = [
        'TPM2_Sign RSA 1024 TPM2_ALG_RSAPSS',
        'TPM2_Sign RSA 1024 TPM2_ALG_RSASSA',
        'TPM2_Sign RSA 2048 TPM2_ALG_RSAPSS',
        'TPM2_Sign RSA 2048 TPM2_ALG_RSASSA',
        'TPM2_VerifySignature RSA 1024 TPM2_ALG_RSAPSS',
        'TPM2_VerifySignature RSA 1024 TPM2_ALG_RSASSA',
        'TPM2_VerifySignature RSA 2048 TPM2_ALG_RSAPSS',
        'TPM2_VerifySignature RSA 2048 TPM2_ALG_RSASSA',
    ]

    ECC = [
        'TPM2_Sign TPM2_ECC_BN_P256 TPM2_ALG_ECDSA',
        'TPM2_Sign TPM2_ECC_BN_P256 TPM2_ALG_ECSCHNORR',
        'TPM2_Sign TPM2_ECC_BN_P256 TPM2_ALG_SM2',
        'TPM2_Sign TPM2_ECC_NIST_P224 TPM2_ALG_ECDSA',
        'TPM2_Sign TPM2_ECC_NIST_P224 TPM2_ALG_ECSCHNORR',
        'TPM2_Sign TPM2_ECC_NIST_P224 TPM2_ALG_SM2',
        'TPM2_Sign TPM2_ECC_NIST_P256 TPM2_ALG_ECDSA',
        'TPM2_Sign TPM2_ECC_NIST_P256 TPM2_ALG_ECSCHNORR',
        'TPM2_Sign TPM2_ECC_NIST_P256 TPM2_ALG_SM2',
        'TPM2_VerifySignature TPM2_ECC_BN_P256 TPM2_ALG_ECDSA',
        'TPM2_VerifySignature TPM2_ECC_BN_P256 TPM2_ALG_ECSCHNORR',
        'TPM2_VerifySignature TPM2_ECC_NIST_P224 TPM2_ALG_ECDSA',
        'TPM2_VerifySignature TPM2_ECC_NIST_P224 TPM2_ALG_ECSCHNORR',
        'TPM2_VerifySignature TPM2_ECC_NIST_P256 TPM2_ALG_ECDSA',
        'TPM2_VerifySignature TPM2_ECC_NIST_P256 TPM2_ALG_ECSCHNORR'
    ]

    ENC = [
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CBC decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CBC decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CBC encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CBC encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CFB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CFB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CFB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CFB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_CTR encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_ECB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_ECB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_ECB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_ECB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB decrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB encrypt',
        'TPM2_EncryptDecrypt TPM2_ALG_AES TPM2_ALG_OFB encrypt',
    ]

    CREATE = [
        'TPM2_Create HMAC',
        'TPM2_Create RSA 1024',
        'TPM2_Create RSA 2048',
        'TPM2_Create TPM2_ALG_AES 128',
        'TPM2_Create TPM2_ALG_AES 192',
        'TPM2_Create TPM2_ALG_AES 256',
        'TPM2_Create TPM2_ECC_BN_P256',
        'TPM2_Create TPM2_ECC_NIST_P224',
        'TPM2_Create TPM2_ECC_NIST_P256',
    ]

    HASH = [
        'TPM2_Hash TPM2_ALG_SHA',
        'TPM2_Hash TPM2_ALG_SHA256',
    ]

    ALL = RSA_ENC_DEC + RSA_SIGN + ECC + ENC + CREATE + HASH

    GROUPS = [RSA_ENC_DEC, RSA_SIGN, ECC, ENC, CREATE, HASH]

    ABBREVIATIONS = ["RSA Enc/Dec", "RSA Sign/Verify", "ECC", "ENC", "CREATE", "HASH"]

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


class TPM2Identifier:
    """Class for parsing hex identifiers of TPM algs and commands"""
    ALG_ID_STR = {
        0x0001: "TPM2_ALG_RSA",
        0x0004: "TPM2_ALG_SHA",
        # Two identical ids
        # 0x0004: "TPM2_ALG_SHA1",
        0x0005: "TPM2_ALG_HMAC",
        0x0006: "TPM2_ALG_AES",
        0x0007: "TPM2_ALG_MGF1",
        0x0008: "TPM2_ALG_KEYEDHASH",
        0x000A: "TPM2_ALG_XOR",
        0x000B: "TPM2_ALG_SHA256",
        0x000C: "TPM2_ALG_SHA384",
        0x000D: "TPM2_ALG_SHA512",
        0x0010: "TPM2_ALG_NULL",
        0x0012: "TPM2_ALG_SM3_256",
        0x0013: "TPM2_ALG_SM4",
        0x0014: "TPM2_ALG_RSASSA",
        0x0015: "TPM2_ALG_RSAES",
        0x0016: "TPM2_ALG_RSAPSS",
        0x0017: "TPM2_ALG_OAEP",
        0x0018: "TPM2_ALG_ECDSA",
        0x0019: "TPM2_ALG_ECDH",
        0x001A: "TPM2_ALG_ECDAA",
        0x001B: "TPM2_ALG_SM2",
        0x001C: "TPM2_ALG_ECSCHNORR",
        0x001D: "TPM2_ALG_ECMQV",
        0x0020: "TPM2_ALG_KDF1_SP800_56A",
        0x0021: "TPM2_ALG_KDF2",
        0x0022: "TPM2_ALG_KDF1_SP800_108",
        0x0023: "TPM2_ALG_ECC",
        0x0025: "TPM2_ALG_SYMCIPHER",
        0x0026: "TPM2_ALG_CAMELLIA",
        0x0040: "TPM2_ALG_CTR",
        0x0027: "TPM2_ALG_SHA3_256",
        0x0028: "TPM2_ALG_SHA3_384",
        0x0029: "TPM2_ALG_SHA3_512",
        0x0041: "TPM2_ALG_OFB",
        0x0042: "TPM2_ALG_CBC",
        0x0043: "TPM2_ALG_CFB",
        0x0044: "TPM2_ALG_ECB",
    }
    ALGS = list(ALG_ID_STR.values())

    CC_STR = {
        0x0000011f: "TPM2_CC_NV_UndefineSpaceSpecial",
        0x00000120: "TPM2_CC_EvictControl",
        0x00000121: "TPM2_CC_HierarchyControl",
        0x00000122: "TPM2_CC_NV_UndefineSpace",
        0x00000124: "TPM2_CC_ChangeEPS",
        0x00000125: "TPM2_CC_ChangePPS",
        0x00000126: "TPM2_CC_Clear",
        0x00000127: "TPM2_CC_ClearControl",
        0x00000128: "TPM2_CC_ClockSet",
        0x00000129: "TPM2_CC_HierarchyChangeAuth",
        0x0000012a: "TPM2_CC_NV_DefineSpace",
        0x0000012b: "TPM2_CC_PCR_Allocate",
        0x0000012c: "TPM2_CC_PCR_SetAuthPolicy",
        0x0000012d: "TPM2_CC_PP_Commands",
        0x0000012e: "TPM2_CC_SetPrimaryPolicy",
        0x0000012f: "TPM2_CC_FieldUpgradeStart",
        0x00000130: "TPM2_CC_ClockRateAdjust",
        0x00000131: "TPM2_CC_CreatePrimary",
        0x00000132: "TPM2_CC_NV_GlobalWriteLock",
        0x00000133: "TPM2_CC_GetCommandAuditDigest",
        0x00000134: "TPM2_CC_NV_Increment",
        0x00000135: "TPM2_CC_NV_SetBits",
        0x00000136: "TPM2_CC_NV_Extend",
        0x00000137: "TPM2_CC_NV_Write",
        0x00000138: "TPM2_CC_NV_WriteLock",
        0x00000139: "TPM2_CC_DictionaryAttackLockReset",
        0x0000013a: "TPM2_CC_DictionaryAttackParameters",
        0x0000013b: "TPM2_CC_NV_ChangeAuth",
        0x0000013c: "TPM2_CC_PCR_Event",
        0x0000013d: "TPM2_CC_PCR_Reset",
        0x0000013e: "TPM2_CC_SequenceComplete",
        0x0000013f: "TPM2_CC_SetAlgorithmSet",
        0x00000140: "TPM2_CC_SetCommandCodeAuditStatus",
        0x00000141: "TPM2_CC_FieldUpgradeData",
        0x00000142: "TPM2_CC_IncrementalSelfTest",
        0x00000143: "TPM2_CC_SelfTest",
        0x00000144: "TPM2_CC_Startup",
        0x00000145: "TPM2_CC_Shutdown",
        0x00000146: "TPM2_CC_StirRandom",
        0x00000147: "TPM2_CC_ActivateCredential",
        0x00000148: "TPM2_CC_Certify",
        0x00000149: "TPM2_CC_PolicyNV",
        0x0000014a: "TPM2_CC_CertifyCreation",
        0x0000014b: "TPM2_CC_Duplicate",
        0x0000014c: "TPM2_CC_GetTime",
        0x0000014d: "TPM2_CC_GetSessionAuditDigest",
        0x0000014e: "TPM2_CC_NV_Read",
        0x0000014f: "TPM2_CC_NV_ReadLock",
        0x00000150: "TPM2_CC_ObjectChangeAuth",
        0x00000151: "TPM2_CC_PolicySecret",
        0x00000152: "TPM2_CC_Rewrap",
        0x00000153: "TPM2_CC_Create",
        0x00000154: "TPM2_CC_ECDH_ZGen",
        0x00000155: "TPM2_CC_HMAC",
        0x00000156: "TPM2_CC_Import",
        0x00000157: "TPM2_CC_Load",
        0x00000158: "TPM2_CC_Quote",
        0x00000159: "TPM2_CC_RSA_Decrypt",
        0x0000015b: "TPM2_CC_HMAC_Start",
        0x0000015c: "TPM2_CC_SequenceUpdate",
        0x0000015d: "TPM2_CC_Sign",
        0x0000015e: "TPM2_CC_Unseal",
        0x00000160: "TPM2_CC_PolicySigned",
        0x00000161: "TPM2_CC_ContextLoad",
        0x00000162: "TPM2_CC_ContextSave",
        0x00000163: "TPM2_CC_ECDH_KeyGen",
        0x00000164: "TPM2_CC_EncryptDecrypt",
        0x00000165: "TPM2_CC_FlushContext",
        0x00000167: "TPM2_CC_LoadExternal",
        0x00000168: "TPM2_CC_MakeCredential",
        0x00000169: "TPM2_CC_NV_ReadPublic",
        0x0000016a: "TPM2_CC_PolicyAuthorize",
        0x0000016b: "TPM2_CC_PolicyAuthValue",
        0x0000016c: "TPM2_CC_PolicyCommandCode",
        0x0000016d: "TPM2_CC_PolicyCounterTimer",
        0x0000016e: "TPM2_CC_PolicyCpHash",
        0x0000016f: "TPM2_CC_PolicyLocality",
        0x00000170: "TPM2_CC_PolicyNameHash",
        0x00000171: "TPM2_CC_PolicyOR",
        0x00000172: "TPM2_CC_PolicyTicket",
        0x00000173: "TPM2_CC_ReadPublic",
        0x00000174: "TPM2_CC_RSA_Encrypt",
        0x00000176: "TPM2_CC_StartAuthSession",
        0x00000177: "TPM2_CC_VerifySignature",
        0x00000178: "TPM2_CC_ECC_Parameters",
        0x00000179: "TPM2_CC_FirmwareRead",
        0x0000017a: "TPM2_CC_GetCapability",
        0x0000017b: "TPM2_CC_GetRandom",
        0x0000017c: "TPM2_CC_GetTestResult",
        0x0000017d: "TPM2_CC_Hash",
        0x0000017e: "TPM2_CC_PCR_Read",
        0x0000017f: "TPM2_CC_PolicyPCR",
        0x00000180: "TPM2_CC_PolicyRestart",
        0x00000181: "TPM2_CC_ReadClock",
        0x00000182: "TPM2_CC_PCR_Extend",
        0x00000183: "TPM2_CC_PCR_SetAuthValue",
        0x00000184: "TPM2_CC_NV_Certify",
        0x00000185: "TPM2_CC_EventSequenceComplete",
        0x00000186: "TPM2_CC_HashSequenceStart",
        0x00000187: "TPM2_CC_PolicyPhysicalPresence",
        0x00000188: "TPM2_CC_PolicyDuplicationSelect",
        0x00000189: "TPM2_CC_PolicyGetDigest",
        0x0000018a: "TPM2_CC_TestParms",
        0x0000018b: "TPM2_CC_Commit",
        0x0000018c: "TPM2_CC_PolicyPassword",
        0x0000018d: "TPM2_CC_ZGen_2Phase",
        0x0000018e: "TPM2_CC_EC_Ephemeral",
        0x0000018f: "TPM2_CC_PolicyNvWritten",
        0x00000190: "TPM2_CC_PolicyTemplate",
        0x00000191: "TPM2_CC_CreateLoaded",
        0x00000192: "TPM2_CC_PolicyAuthorizeNV",
        0x00000193: "TPM2_CC_EncryptDecrypt2",
        0x00000194: "TPM2_CC_AC_GetCapability",
        0x00000195: "TPM2_CC_AC_Send",
        0x00000196: "TPM2_CC_Policy_AC_SendSelect",
    }
    CCS = list(CC_STR.values())

    ECC_CURVE_STR = {
        0x0001: "TPM2_ECC_NIST_P192",
        0x0002: "TPM2_ECC_NIST_P224",
        0x0003: "TPM2_ECC_NIST_P256",
        0x0004: "TPM2_ECC_NIST_P384",
        0x0005: "TPM2_ECC_NIST_P521",
        0x0010: "TPM2_ECC_BN_P256",
        0x0011: "TPM2_ECC_BN_P638",
        0x0020: "TPM2_ECC_SM2_P256",
    }
    ECC_CURVES = list(ECC_CURVE_STR.values())

    ALL_KEYS = ALGS + CCS + ECC_CURVES


CARD_EXCEPTION_TO_STRING = {
    'f101': 'CryptoException_ILLEGAL_VALUE',
    'f102': 'CryptoException_UNINITIALIZED_KEY',
    'f103': 'CryptoException_NO_SUCH_ALGORITHM',
    'f104': 'CryptoException_INVALID_INIT',
    'f105': 'CryptoException_ILLEGAL_USE',
    'f201': 'SystemException_ILLEGAL_VALUE',
    'f202': 'SystemException_NO_TRANSIENT_SPACE',
    'f203': 'SystemException_ILLEGAL_TRANSIENT',
    'f204': 'SystemException_ILLEGAL_AID',
    'f205': 'SystemException_NO_RESOURCE',
    'f206': 'SystemException_ILLEGAL_USE',
    'f301': 'PINException_ILLEGAL_VALUE',
    'f302': 'PINException_ILLEGAL_STATE',
    'f401': 'TransactionException_IN_PROGRESS',
    'f402': 'TransactionException_NOT_IN_PROGRESS',
    'f403': 'TransactionException_BUFFER_FULL',
    'f404': 'TransactionException_INTERNAL_FAILURE',
    'f405': 'TransactionException_ILLEGAL_USE',
    'f500': 'CardRuntimeException',
    'ff01': 'Exception_GENERIC',
    'ff02': 'ArrayIndexOutOfBoundsException',
    'ff03': 'ArithmeticException',
    'ff04': 'ArrayStoreException',
    'ff05': 'NullPointerException',
    'ff06': 'NegativeArraySizeException',
    'ff': 'Exception_GENERIC',
    '6a81': 'FUNC_NOT_SUPPORTED',
    '6f00': 'Exception_GENERIC'
}
