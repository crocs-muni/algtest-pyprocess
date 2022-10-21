import io

import matplotlib.pyplot as plt
from matplotlib.pyplot import close
import numpy as np


class Spectrogram:

    def __init__(self, df, device_name, xsys=None, title=None):
        xsys = self.compute_xsys if not xsys else xsys
        self.xs, self.ys = xsys(df)
        self.device_name = device_name
        self.fig = None
        self.title = None

    def compute_xsys(self, df):
        nonce_bytes = list(map(lambda x: int(x[:2], 16), list(df.nonce)))
        duration = list(df.duration)
        return nonce_bytes, duration

    def mapper(self):
        counts = {}
        total  = {x : 0 for x in range(256)}
        # First ve count durations which hit particular byte
        for x, y in zip(self.xs, self.ys):
            # 1000 is milliseconds
            key = (x, round(y * 1000, 1))
            counts.setdefault(key, 0)
            counts[key] += 1
            total[x] += 1
        # Secondly we create colormesh
        X = list(range(256))
        # If u make Y as a range(min, max) we wont
        # have problems with big rectangles in output
        y = list(map(lambda x: x[1], counts.keys()))
        Y = list(map(lambda x: round(x * 10) / 10, np.arange(min(y), max(y), 0.1)))
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
            f"Nonce MSB vs signature time - {self.device_name}"
        )
        ax.pcolormesh(X, Y, Z)

        ax.set_xticks([16, 32, 128, 256])
        ax.set_xlabel("nonce MSB value")
        ax.set_ylabel("signature duration in milliseconds")

    def build(self):
        """Builds the spectrogram so it can be saved or shown"""
        self.spectrogram()
        return self

    def show(self):
        """Shows the heatmap"""
        plt.show()

    def svg(self):
        """Saves svg as string"""
        f = io.BytesIO()
        plt.savefig(f, format="svg")
        value = f.getvalue()
        f.close()
        self.finalize()
        return value.decode('ascii')

    def save(self, filename: str, format: str = 'png'):
        plt.savefig(filename, format=format)
        self.finalize()

    def finalize(self):
        close(self.fig)
        self.fig = None
