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

    def __add__(self, other):
        assert isinstance(other, CryptoProps)
        new = CryptoProps(f"{self.path}:{other.path}")
        new.manufacturer = self.manufacturer
        new.vendor_string = self.vendor_string
        new.firmware_version = self.firmware_version
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

    def _plot(self, plot, algs, output_path, allowed_algs, fname, pname):
        if not algs:
            algs = allowed_algs

        if set(algs) - allowed_algs != set():
            logging.warning(
                f"{fname}:{self.path} trying to build {pname} for some unallowed algs")
            return
        for alg in algs:
            if self.results.get(alg) is None:
                logging.info(f"{fname}:{self.path} has no {alg.value}")
                continue
            df = self.results.get(alg).data
            assert df is not None
            assert os.path.exists(os.path.join(output_path))
            try:
                plot(df)().build().save(
                    os.path.join(output_path, f"{pname}_{alg.value}.png"),
                    'png'
                )
            except BaseException as e:
                logging.warning(
                    f"{fname}:{self.path} {pname} build failed for {alg.value}, {str(e)}")
            gc.collect()

    def plot_heatmaps(self,
                      algs: List[CryptoPropResultCategory],
                      output_path: str,
                      title: str = ""):
        allowed = {CryptoPropResultCategory.RSA_1024,
                   CryptoPropResultCategory.RSA_2048}

        def plot_f(df):
            return partial(
                Heatmap,
                rsa_df=df,
                device_name=self.device_name,
                title=title
            )

        self._plot(plot_f, algs, output_path, allowed, "plot_heatmaps",
                   "heatmap")

    def plot_spectrograms(self,
                          algs: List[CryptoPropResultCategory],
                          output_path: str,
                          title: str = ""):
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

        def plot_f(df):
            return partial(
                Spectrogram,
                df=df,
                device_name=self.device_name,
                title=title
            )

        self._plot(plot_f, algs, output_path, allowed, "plot_spectrograms",
                   "spectrogram")
