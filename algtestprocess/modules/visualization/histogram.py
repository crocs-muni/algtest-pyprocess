import pandas as pd
from typing import Callable, Dict, List, Optional, Tuple, Union
from algtestprocess.modules.visualization.plot import Plot
from overrides import overrides
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np


def get_msb_from_hexstring(hexstring: str) -> int:
    x = int(hexstring, 16)
    return x >> (
        x.bit_length() - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8)
    )


Occurences = List[Union[int, float]]
Title = XLabel = YLabel = LegendLabel = str
Bins = int
Density = bool
RSAValuesPlotData = Tuple[Occurences, Title, XLabel, YLabel, LegendLabel, Bins, Density]


class RSAValues(Plot):
    def __init__(self, grid: Optional[Tuple[int, int]] = None):
        """
        Constructor of the RSAValues class
        :param grid: Tuple signifying the (rows, cols) of resulting plot
        """
        super().__init__()
        self.plots_data: Dict[str, List[RSAValuesPlotData]] = {}
        if grid:
            self.rows, self.cols = grid
        else:
            self.rows = None
            self.cols = None

    def add_keygen_time_distribution(
        self,
        df: pd.DataFrame,
        rsa: int = 1024,
        bins: int = 1000,
        title: str = "Time of the key generation",
        time_unit: Tuple[str, int] = ("ms", 1000),
        name: str = "time distribution",
        density: bool = True,
    ):
        """
        :param df: pandas dataframe
        :param rsa: rsa bits
        :param bins: histogram bins
        :param title: title of the plot
        :param time_unit: name and the constant to multiply timo in seconds with
        """
        assert not df.empty

        unit, constant = time_unit
        time: List[Union[int, float]] = list(
            map(lambda x: round(float(x) * constant), df.t)
        )

        self.add_to_plots_data(
            time,
            title,
            f"time in {unit}",
            "Density (%)",
            f"RSA {rsa}",
            name,
            bins,
            density,
        )

    def add_value_mix_distribution(
        self,
        df: pd.DataFrame,
        rsa: int = 1024,
        getval_f: Callable[
            [str | int | float], Union[int, float]
        ] = get_msb_from_hexstring,
        columns: List[str] = ["n", "d"],
        title: str = "MSBs of modulus N vs private d",
        xlabel: str = "MSB value",
        ylabel: str = "Density",
        name: str = "MSB 1024 Nd",
        bins: int = 1000,
        density: bool = False,
    ):
        """
        :param df: pandas dataframe
        :param rsa: rsa bits
        :param getval_f: function which maps the columns from df into values for dataframe
        :param columns: which will be plotted into histogram plot
        :param title: title of the plot
        :param xlabel: laxel for x axis
        :param ylabel: laxel for y axis
        :param name: id of the plot
        :param bins: histogram bins
        """
        assert not df.empty

        for col in columns:
            xx: List[Union[int, float]] = list(
                map(lambda x: getval_f(x), list(df[col]))
            )
            xxx = {}
            for x in xx:
                xxx.setdefault(x, 0)
                xxx[x] += 1
            print((col, xxx))
            self.add_to_plots_data(
                xx,
                title,
                xlabel,
                ylabel,
                label=col,
                name=name,
                bins=bins,
                density=density,
            )

    def add_to_plots_data(
        self,
        xx: List[Union[int, float]],
        title: str,
        xlabel: str,
        ylabel: str,
        label: str,
        name: str,
        bins: int,
        density: bool,
    ):
        assert xx and title and xlabel and ylabel and label
        self.plots_data.setdefault(name, [])
        self.plots_data[name].append((xx, title, xlabel, ylabel, label, bins, density))

    def histogram(self, ax: plt.Axes, data: List[RSAValuesPlotData]):
        set_metadata = False
        for (xx, title, xlabel, ylabel, label, bins, density) in data:
            ax.hist(xx, density=density, bins=bins, label=label, alpha=0.5)

            if not set_metadata:
                set_metadata = True
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
        ax.legend()

    def subplots(self, axes: np.ndarray):
        assert self.fig is not None
        assert self.cols is not None and self.rows is not None

        items: List[List[RSAValuesPlotData]] = [
            pl_data for _, pl_data in self.plots_data.items()
        ]
        assert items

        i = 0
        for y in range(self.rows):
            for x in range(self.cols):
                if i < len(items):
                    self.histogram(axes[y, x], items[i])
                    i += 1
                else:
                    self.fig.delaxes(axes[y, x])

    @overrides
    def plot(self):
        if not self.rows or not self.cols:
            self.rows = len(self.plots_data) // 2 + 1
            self.cols = 2

        fig, axes = plt.subplots(ncols=self.cols, nrows=self.rows, figsize=(19, 19))
        self.fig = fig
        self.subplots(axes)
