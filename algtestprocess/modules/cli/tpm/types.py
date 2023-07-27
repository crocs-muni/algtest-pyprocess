from typing import Dict, List, Union

Hashes = List[str]
ReportEntry = Dict[str, Union[str, List[str]]]
"""
{
    "TPM name": str,
    "vendor": str,
    "title": str,
    "measurement paths": List[str]
}
"""
ReportMetadata = Dict[str, Union[Dict[str, ReportEntry], Hashes]]
"""
{
    "hashes" = List[str],
    "entries" = Dict[tpm_name||key, ReportEntry]
}
"""
Date = str
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
TPMName = str