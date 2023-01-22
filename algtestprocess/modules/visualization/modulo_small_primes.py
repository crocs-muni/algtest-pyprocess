from ctypes import ArgumentError
from math import sqrt
from typing import Dict, List, Optional, Tuple
from overrides import overrides
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes
import numpy as np
from pandas.core.ops import logical_op

from algtestprocess.modules.visualization.plot import Plot


class ModulusSmallPrimes(Plot):
    def __init__(
        self,
        df: DataFrame,
        title: str,
        primes: List[int] = [11, 13, 17, 19],
        ll_primes: Optional[List[List[int]]] = None,
        grid: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Constructor of ModulusSmallPrimes plot

        :param df: pandas dataframe containing the modulus n field
        :param title: title of the plot
        :param primes: list of primes
        :param ll_primes: list of list of primes
        :param grid: grid of resulting plot (self.rows, self.cols)
        """
        self.n = list(map(lambda x: int(x, 16), df.n))
        self.title = title

        self.primes = primes
        self.ll_primes = ll_primes

        if not grid:
            self.rows, self.cols = self.infer_grid()
        else:
            self.rows, self.cols = grid

    def infer_grid(self) -> Tuple[int, int]:
        if self.ll_primes:
            return 2, len(self.ll_primes) // 2 + 1
        return 1, 1

    def compute_distributions(self, primes: List[int]) -> Dict[int, Dict[int, float]]:
        """
        Method which computes the distribution of the remainders modulo small primes

        :param primes: list of primes
        :returns distribution per remainder r per prime p
        """
        assert all([n % p != 0 for n in self.n for p in primes])

        occurences = {p: {r: 0 for r in range(1, p)} for p in primes}
        # For each prime and modulus count occurence of remainders
        for p in primes:
            for n in self.n:
                occurences[p][n % p] += 1

        # Now we normalize the data
        total = len(self.n)
        distribution = {p: {r: float(0) for r in range(1, p)} for p in primes}
        for p in primes:
            for r in range(1, p):
                distribution[p][r] = occurences[p][r] / total
        return distribution

    def mod_small_primes_plot(self, ax: Axes, primes: List[int]) -> None:
        """
        Draws one subplot of ModuloSmallPrimes visualization

        :param ax: matplotlib ax on which we plot
        :param primes: list of primes
        """
        distribution = self.compute_distributions(primes)

        ax.set_prop_cycle(
            "color", [plt.cm.Set1(i) for i in np.linspace(0, 1, len(primes))]
        )

        for p, remainders in distribution.items():
            xx = [x[0] for x in remainders.items()]
            yy = [x[1] for x in remainders.items()]
            ax.plot(xx, yy, label=f"( mod {p})", ls="-", marker="o", lw=2)

        ax.legend()
        ax.set_xticks(list(range(1, max(primes))))
        ax.set_xlabel("Remainder")
        ax.set_ylabel("Probability")

    def subplots(self, axes: np.ndarray) -> None:
        """
        Iterates over each list of primes to create its subplot

        :param axes: array of axes to plot on
        """
        assert self.ll_primes

        i = 0
        for x in range(self.cols):
            for y in range(self.rows):
                if i < len(self.ll_primes):
                    self.mod_small_primes_plot(axes[x, y], self.ll_primes[i])
                    i += 1
                else:
                    self.fig.delaxes(axes[x, y])

    @overrides
    def plot(self):
        fig, axes = plt.subplots(self.cols, self.rows, figsize=(19, 19))
        self.fig = fig
        if self.ll_primes:
            self.subplots(axes)
        else:
            assert isinstance(axes, Axes)
            self.mod_small_primes_plot(axes, self.primes)
