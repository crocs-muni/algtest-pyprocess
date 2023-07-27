from typing import List, Tuple
from overrides import overrides

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, Series

from algtestprocess.modules.visualization.plot import Plot


class Spectrogram(Plot):
    def __init__(
        self,
        df,
        device_name=None,
        xsys=None,
        title="Nonce MSB vs Signature duration",
        yrange=(None, None),
        xlabel="nonce MSB value",
        ylabel="signature duration (μs)",
        time_unit=1000000,
        cmap="gnuplot",
    ):
        """
        Constructor of Spectrogram Class

        :param df: pandas dataframe containing nonce and signature duration
        :param device_name: device name
        :param xsys: possibly a function to get the byte and duration values
        :param title: Title of resulting plot
        :param yrange: maximum and minimum value for y
        :param xlabel: x axis label
        :param ylabel: y axis label
        :param time_unit: constant used for changing precision when drawing
        the plot and at the same time conversion of seconds to microseconds
        :param cmap: matplotlib colormap string name
        """
        super().__init__()
        xsys = self.compute_xsys if not xsys else xsys
        self.xs, self.ys = xsys(df)
        self.device_name = device_name
        self.fig = None
        self.title = title
        self.time_unit = time_unit
        # Set ymin ymax manually
        self.ymin, self.ymax = yrange
        # Round and set ymin, ymax if it wasnt done so before
        self.ymin, self.ymax = self.round_yminymax(df)
        self.cmap = cmap
        self.xlabel = xlabel
        self.ylabel = ylabel

    def round_yminymax(self, df: DataFrame) -> Tuple[float, float]:
        """
        Rounds the maximal and minimal durations of signatures.

        :param df: pandas dataframe containing signature durations
        :returns: rounded max and min duration

        """
        if self.ymin is None or self.ymax is None:
            self.ymin = Series(df["duration"] + df["duration_extra"]).nsmallest(5).max()
            self.ymax = Series(df["duration"] + df["duration_extra"]).nlargest(5).min()

        return (
            round(self.ymin * self.time_unit),
            round(self.ymax * self.time_unit),
        )

    def compute_xsys(self, df: DataFrame):
        """
        Computes the most significant bytes of nonce from given dataframe
        and returns them along with signature durations

        :param df: dataframe containing nonces
        :returns: tuple of nonce MSBs and signature durations

        """
        # assert all(map(lambda x: len(x) % 2 == 0, df.nonce))
        df = df.dropna(subset=['nonce', 'duration', 'duration_extra'])
        
        if len(df) < 1:
            raise ValueError("visualized dataframe must not be empty")
        
        nonce_bytes = list(map(lambda x: int(x, 16), list(df.nonce)))
        nonce_bytes = list(
            map(
                lambda x: x
                >> x.bit_length()
                - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8),
                nonce_bytes,
            )
        )
        duration = list(df.duration + df.duration_extra)
        return nonce_bytes, duration

    def mapper(self) -> Tuple[List[int], List[float], List[List[int]]]:
        """
        Remaps two dimensional data [msb of nonce, signature duration] to
        three dimensional data [msb of nonce, signature duration, occurences]

        :returns:  X values, Y values, and 2D array of size len(X)*len(Y)
        """
        counts = {}
        total = {x: 0 for x in range(256)}
        # First ve count durations which hit particular byte
        for x, y in zip(self.xs, self.ys):
            key = (x, round(y * self.time_unit))
            counts.setdefault(key, 0)
            counts[key] += 1
            total[x] += 1

        # Secondly we create colormesh
        X = list(range(256))
        Y = list(range(self.ymin, self.ymax))

        Z = []
        added = 0
        for d in Y:
            ZZ = []
            for n in X:
                k = (n, d)
                val = counts.get(k)
                if val:
                    added += 1
                    ZZ.append(val)
                else:
                    ZZ.append(0)
            Z.append(ZZ)
        return X, Y, Z

    def spectrogram(self) -> None:
        """Draws the spectrogram visualization"""
        X, Y, Z = self.mapper()

        fig = plt.figure(figsize=(24, 15))
        self.fig = fig

        ax = fig.add_subplot()

        plt.title(
            f"{self.title}" + (f"\n{self.device_name}" if self.device_name else ""),
            fontsize=40,
        )

        pcm = ax.pcolormesh(X, Y, Z, cmap=self.cmap)
        fig.colorbar(pcm, ax=ax, format="%d", spacing="proportional")

        ax.set_xticks([8, 16, 32, 64, 128, 255], fontsize=20)
        ax.vlines([8, 16, 32, 64, 128], ymin=self.ymin, ymax=self.ymax, color="white")

        ax.set_xlabel(self.xlabel, fontsize=32)
        ax.set_ylabel(self.ylabel, fontsize=32)

    @overrides
    def plot(self):
        self.spectrogram()
