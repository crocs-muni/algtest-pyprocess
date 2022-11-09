from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, List, Union, Callable

from overrides import EnforceOverrides, overrides

def null_if_none(x: any):
    return 'null' if x is None else x

def bool_to_tf(x: bool) -> str:
    return 'true'if x else 'false'

def null_if_exc(f: Callable):
    try:
        return f()
    except Exception:
        return 'null'

class MeasurementResultJC(ABC, EnforceOverrides):
    """
    Base class for result storage
    """

    def __init__(self):
        self.name: Optional[str] = None
        self.category: Optional[Union[MeasurementCategory, str]] = None
        self.error: Optional[str] = None

    def export(self):
        category = str(self.category.value) \
            if isinstance(self.category, Enum) \
            else null_if_none(self.category)

        return {
            "name": null_if_none(self.name),
            "category": category,
            "error": null_if_none(self.error)
        }



class PerformanceResultJC(MeasurementResultJC):
    """
    Most of this class comes from crocs-muni/scrutiny on Github

    Class to store results of algorithm performance testing
    """

    def __init__(self) -> None:
        super().__init__()
        self.prepare_ins: Optional[str] = None
        self.measure_ins: Optional[str] = None
        self.config: Optional[str] = None

        self.baseline: List[float] = []
        self.operation: List[float] = []

        self.data_length: Optional[int] = None
        self.iterations: Optional[int] = None
        self.invocations: Optional[int] = None

    def baseline_avg(self) -> float:
        """Average baseline measurement"""
        return sum(self.baseline) / len(self.baseline)

    def baseline_min(self) -> float:
        """Minimal baseline measurement"""
        return min(self.baseline)

    def baseline_max(self) -> float:
        """Maximal baseline measurement"""
        return max(self.baseline)

    def ipm(self) -> int:
        """
        Algorithm iterations per measurement
        :return: iterations / len(operation)
        """
        if self.iterations % len(self.operation) != 0:
            raise Exception(
                "Total iterations count is not "
                "multiple of operation data length"
            )
        return max(1, int(self.iterations / len(self.operation)))

    def operation_avg(self) -> float:
        """Average single algorithm execution time"""
        return sum(self.operation) / len(self.operation) / self.ipm()

    def operation_min(self) -> float:
        """Minimal single algorithm execution time"""
        return min(self.operation) / self.ipm()

    def operation_max(self) -> float:
        """Maximal single algorithm execution time"""
        return max(self.operation) / self.ipm()

    @overrides
    def export(self):
        data = super(PerformanceResultJC, self).export()
        data.update({
            "baseline_avg": null_if_exc(self.baseline_avg),
            "baseline_min": null_if_exc(self.baseline_min),
            "baseline_max": null_if_exc(self.baseline_max),
            "operation_avg": null_if_exc(self.operation_avg),
            "operation_min": null_if_exc(self.operation_min),
            "operation_max": null_if_exc(self.operation_max),
        })
        return data


class SupportResultJC(MeasurementResultJC):
    """
    Most of this class comes from crocs-muni/scrutiny on Github

    Class to store results of algorithm support testing
    """

    def __init__(self):
        super().__init__()
        self.support: Optional[bool] = None
        self.time_elapsed: Optional[float] = None
        self.persistent_memory: Optional[int] = None
        self.ram_deselect: Optional[int] = None
        self.ram_reset: Optional[int] = None

    @overrides
    def export(self):
        data = super(SupportResultJC, self).export()
        data.update({
            "support": bool_to_tf(self.support),
            "time_elapsed": null_if_none(self.time_elapsed),
            "persistent_memory": null_if_none(self.persistent_memory),
            "ram_deselect": null_if_none(self.ram_deselect),
            "ram_reset": null_if_none(self.ram_reset)
        })
        return data


MethodName = str


class ProfileJC(ABC, EnforceOverrides):
    """Profile base class"""

    def __init__(self):
        self.test_info = {}
        self.jcsystem = {}
        self.cplc = {}

    def device_name(self):
        return self.test_info.get('Card name')

    def rename(self, name: str):
        self.test_info['Card name'] = name

    @abstractmethod
    def add_result(self, key: MethodName, result: MeasurementResultJC):
        pass

    def export(self):
        return {
            "test_info": self.test_info,
            "jcsystem": self.jcsystem,
            "cplc": self.cplc
        }


class ProfilePerformanceFixedJC(ProfileJC):
    """Java card profile with fixed data length results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[MethodName, PerformanceResultJC] = {}

    @overrides
    def add_result(self, key: MethodName, result: MeasurementResultJC):
        self.results[key] = result

    @overrides
    def export(self):
        data = super(ProfilePerformanceFixedJC, self).export()
        data.update({
            "results_type": "performance fixed",
            "results": [result.export() for result in self.results.values()]
        })
        return data


class ProfilePerformanceVariableJC(ProfileJC):
    """Java card profile with variable data length results"""

    def __init__(self):
        super().__init__()
        self.results: Dict[MethodName, List[PerformanceResultJC]] = {}

    @overrides
    def add_result(self, key: MethodName, result: MeasurementResultJC):
        if key not in self.results:
            self.results[key] = []
        self.results[key].append(result)

    @overrides
    def export(self):
        data = super(ProfilePerformanceVariableJC, self).export()
        data.update({
            "results_type": "performance variable",
            "results": [
                [result.export() for result in results]
                for results in self.results.values()
            ]
        })
        return data

class ProfileSupportJC(ProfileJC):
    """Java card profile with support results"""
    def __init__(self):
        super().__init__()
        self.results: Dict[MethodName, SupportResultJC] = {}

    @overrides
    def add_result(self, key: MethodName, result: MeasurementResultJC):
        self.results[key] = result

    @overrides
    def export(self):
        data = super(ProfileSupportJC, self).export()
        data.update({
            "results_type": "support",
            "results": [result.export() for result in self.results.values()]
        })


class MeasurementCategory(Enum):
    """Measurement category enum"""

    MESSAGE_DIGEST = "MESSAGE DIGEST"
    RANDOM_GENERATOR = "RANDOM GENERATOR"
    CIPHER = "CIPHER"
    SIGNATURE = "SIGNATURE"
    CHECKSUM = "CHECKSUM"
    AESKEY = "AESKey"
    DESKEY = "DESKey"
    KOREANSEEDKEY = "KoreanSEEDKey"
    DSAPRIVATEKEY = "DSAPrivateKey"
    DSAPUBLICKEY = "DSAPublicKey"
    ECF2MPUBLICKEY = "ECF2MPublicKey"
    ECF2MPRIVATEKEY = "ECF2MPrivateKey"
    ECFPPRIVATEKEY = "ECFPPrivateKey"
    ECFPPUBLICKEY = "ECFPPublicKey"
    HMACKEY = "HMACKey"
    RSAPRIVATEKEY = "RSAPrivateKey"
    RSAPUBLICKEY = "RSAPublicKey"
    RSAPRIVATECRTKEY = "RSAPrivateCRTKey"
    KEY_PAIR = "KEY PAIR"
    UTIL = "UTIL"
    SWALGS = "SWALGS"
    KEYAGREEMENT = "KEYAGREEMENT"
