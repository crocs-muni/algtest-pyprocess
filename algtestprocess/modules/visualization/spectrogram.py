from locale import normalize
from overrides import overrides

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from pandas import Series

from algtestprocess.modules.visualization.plot import Plot


class Spectrogram(Plot):
    def __init__(
        self,
        df,
        device_name,
        xsys=None,
        title="",
        yrange=(None, None),
        time_unit=1000000,
        cmap="gnuplot",
    ):
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

    def round_yminymax(self, df):
        if self.ymin is None or self.ymax is None:
            self.ymin = Series(df["duration"]).nsmallest(5).max()
            self.ymax = Series(df["duration"]).nlargest(5).min()

        return (
            round(self.ymin * self.time_unit),
            round(self.ymax * self.time_unit),
        )

    def compute_xsys(self, df):
        # assert all(map(lambda x: len(x) % 2 == 0, df.nonce))
        nonce_bytes = list(map(lambda x: int(x, 16), list(df.nonce)))
        nonce_bytes = list(
            map(
                lambda x: x
                >> x.bit_length()
                - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8),
                nonce_bytes,
            )
        )
        duration = list(df.duration)
        return nonce_bytes, duration

    def mapper(self):
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

    def spectrogram(self):
        X, Y, Z = self.mapper()

        fig = plt.figure(figsize=(24, 15))
        self.fig = fig

        ax = fig.add_subplot()

        plt.title(
            f"Nonce MSB vs signature time\n{self.device_name}\n{self.title}",
            fontsize=40,
        )
        pcm = ax.pcolormesh(X, Y, Z, cmap=self.cmap)
        fig.colorbar(pcm, ax=ax, format="%d")

        ax.set_xticks([16, 32, 128, 256], fontsize=20)

        ax.set_xlabel("nonce MSB value", fontsize=32)
        ax.set_ylabel("signature duration (μs)", fontsize=32)

    @overrides
    def plot(self):
        self.spectrogram()
