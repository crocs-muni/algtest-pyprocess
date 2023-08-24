import gc
import logging
import os
from functools import partial
from typing import Dict, List, Optional

from overrides import overrides

from algtestprocess.modules.data.tpm.enums import CryptoPropResultCategory
from algtestprocess.modules.data.tpm.profiles.base import ProfileTPM
from algtestprocess.modules.data.tpm.results.cryptoprops import CryptoPropResult
from algtestprocess.modules.visualization.heatmap import Heatmap
from algtestprocess.modules.visualization.spectrogram import Spectrogram


class CryptoProps(ProfileTPM):

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.results: Dict[CryptoPropResultCategory, CryptoPropResult] = {}
        self.merged = False

    @overrides
    def add_result(self, result):
        assert result.category
        category = result.category
        if not self.results.get(category):
            self.results[category] = result

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    
    def __add__(self, other):
        assert isinstance(other, CryptoProps)
        new = CryptoProps(f"{self.path}:{other.path}")
        # Makes sense to merge only same vendors. 
        assert self.manufacturer == other.manufacturer
        new.manufacturer = self.manufacturer
        # If we merge same TPMs we can len the vendor string be
        if self.vendor_string == other.vendor_string:
            new.vendor_string = self.vendor_string
        else:
            new.vendor_string = ''
        
        if not isinstance(self.firmware_version, list) and self.firmware_version == other.firmware_version:
            fw = self.firmware_version
        else:
            if isinstance(self.firmware_version, list):
                fw = self.firmware_version
            else:
                fw = [self.firmware_version]
            fw.extend(other.firmware_version if isinstance(other.firmware_version, list) else [other.firmware_version])
            fw.sort(key=lambda x: x.split('.'))
        new.firmware_version = fw
        new.merged = True

        for alg in CryptoPropResultCategory.list():
            my_result = self.results.get(alg)
            other_result = other.results.get(alg)

            if my_result is None and other_result is None:
                continue

            if my_result is None:
                new.results[alg] = other_result
                continue

            if other_result is None:
                new.results[alg] = my_result
                continue

            new.results[alg] = my_result + other_result
        return new

    def _plot(self, plot, algs, output_path, allowed_algs, fname, pname, save):
        if not algs:
            algs = allowed_algs

        if set(algs) - allowed_algs != set():
            logging.warning(
                f"{fname}:{self.path} trying to build {pname} for some unallowed algs")
            return
        plots = []
        for alg in algs:
            if self.results.get(alg) is None:
                logging.info(f"{fname}:{self.path} has no {alg.value}")
                continue
            df = self.results.get(alg).data
            assert df is not None
            if save:
                assert os.path.exists(os.path.join(output_path))
            try:
                title = f"{alg.value.replace('_', ' ').upper()}, {len(df.index)} entries"
                p = plot(df, title)().build()

                if save:
                    p.save(
                        os.path.join(output_path, f"{pname}_{alg.value}.png"),
                        'png'
                    )
                else:
                    plots.append(p)
            except Exception as e:
                logging.warning(
                    f"{fname}:{self.path} {pname} build failed for {alg.value}, {str(e)}")
            gc.collect()
        return plots

    def plot_heatmaps(self,
                      algs: List[CryptoPropResultCategory],
                      output_path: Optional[str] = ".",
                      save: bool = False):
        allowed = {CryptoPropResultCategory.RSA_1024,
                   CryptoPropResultCategory.RSA_2048}

        def plot_f(df, title):
            return partial(
                Heatmap,
                rsa_df=df,
                device_name=self.device_name,
                title=title
            )

        return self._plot(plot_f, algs, output_path, allowed, "plot_heatmaps",
                          "heatmap", save)

    def plot_spectrograms(self,
                          algs: List[CryptoPropResultCategory],
                          output_path: Optional[str] = ".",
                          save: bool = False):
        allowed = {
            CryptoPropResultCategory.ECC_P256_ECDSA,
            CryptoPropResultCategory.ECC_P256_ECDAA,
            CryptoPropResultCategory.ECC_P256_ECSCHNORR,
            CryptoPropResultCategory.ECC_P384_ECDSA,
            CryptoPropResultCategory.ECC_P384_ECDAA,
            CryptoPropResultCategory.ECC_P384_ECSCHNORR,
            CryptoPropResultCategory.ECC_BN256_ECDSA,
            CryptoPropResultCategory.ECC_BN256_ECDAA,
            CryptoPropResultCategory.ECC_BN256_ECSCHNORR
        }

        def plot_f(df, title):
            return partial(
                Spectrogram,
                df=df,
                device_name=self.device_name,
                title=title
            )

        return self._plot(plot_f, algs, output_path, allowed,
                          "plot_spectrograms",
                          "spectrogram", save)
