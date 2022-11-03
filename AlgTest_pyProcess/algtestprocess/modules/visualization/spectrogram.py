from overrides import overrides

import matplotlib.pyplot as plt
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
        time_unit=1000,
        precision=1,
    ):
        super().__init__()
        xsys = self.compute_xsys if not xsys else xsys
        self.xs, self.ys = xsys(df)
        self.device_name = device_name
        self.fig = None
        self.title = title
        self.precision = precision
        self.time_unit = time_unit
        # Set ymin ymax manually
        self.ymin, self.ymax = yrange
        # Round and set ymin, ymax if it wasnt done so before
        self.ymin, self.ymax = self.round_yminymax(df)

    def round_yminymax(self, df):
        if self.ymin is None or self.ymax is None:
            self.ymin = Series(df["duration"]).nsmallest(5).max()
            self.ymax = Series(df["duration"]).nlargest(5).min()

        return (
            round(self.ymin * self.time_unit, self.precision),
            round(self.ymax * self.time_unit, self.precision),
        )

    def compute_xsys(self, df):
        nonce_bytes = list(map(lambda x: int(x[:2], 16), list(df.nonce)))
        duration = list(df.duration)
        return nonce_bytes, duration

    def mapper(self):
        counts = {}
        total = {x: 0 for x in range(256)}
        # First ve count durations which hit particular byte
        for x, y in zip(self.xs, self.ys):
            key = (x, round(y * self.time_unit, self.precision))
            counts.setdefault(key, 0)
            counts[key] += 1
            total[x] += 1

        # Secondly we create colormesh
        X = list(range(256))
        Y = list(
            map(
                lambda x: round(x * self.time_unit) / self.time_unit,
                np.arange(self.ymin, self.ymax, 10 ** (-self.precision)),
            )
        )

        Z = []
        for d in Y:
            ZZ = []
            for n in X:
                k = (n, d)
                val = counts.get(k)
                if val:
                    ZZ.append(val / total[n])
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
        ax.pcolormesh(X, Y, Z, cmap="gnuplot", rasterized=True)

        ax.set_xticks([16, 32, 128, 256], fontsize=12)
        ax.set_xlabel("nonce MSB value", fontsize=24)

        ax.set_ylabel("signature duration in milliseconds", fontsize=24)

    @overrides
    def plot(self):
        self.spectrogram()
