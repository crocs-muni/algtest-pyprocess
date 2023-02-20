import pandas as pd
from typing import Callable, Dict, List, Optional, Tuple, Union
from algtestprocess.modules.visualization.plot import Plot
from overrides import overrides
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np


Occurences = List[Union[int, float]]
Title = XLabel = YLabel = LegendLabel = str
Bins = int
Density = bool
HistData = Tuple[Occurences, Title, XLabel, YLabel, LegendLabel, Bins, Density]


class HistogramMix(Plot):
    def __init__(self, grid: Optional[Tuple[int, int]] = None):
        """
        Constructor of the HistogramMix class
        :param grid: Tuple signifying the (rows, cols) of resulting plot
        """
        super().__init__()
        self.plots_data: Dict[str, List[HistData]] = {}
        if grid:
            self.rows, self.cols = grid
        else:
            self.rows = None
            self.cols = None

    def add_distribution(
        self,
        df: pd.DataFrame,
        col: str,
        plot_id: str,
        title: str = "Time of the key generation",
        xlabel: XLabel = "time",
        ylabel: YLabel = "number of occurences",
        legend: LegendLabel = "unknown",
        bins: int = 1000,
        density: bool = True,
    ):
        """
        :param df: pandas dataframe
        :param col: column in df containing the values
        :param plot_id: which plot does data belong to
        :param xlabel: label for x axis
        :param ylabel: label for y axis
        :param legend: legend for particular distribution
        :param bins: histogram bins
        :param title: title of the plot
        """
        assert not df.empty
        assert col in df.columns

        self.add_to_plots_data(
            df[col],
            title,
            xlabel,
            ylabel,
            legend,
            plot_id,
            bins,
            density,
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
        if not isinstance(xx, list):
            xx = list(xx)
        assert xx
        assert title and xlabel and ylabel and label
        self.plots_data.setdefault(name, [])
        self.plots_data[name].append((xx, title, xlabel, ylabel, label, bins, density))

    def histogram(self, ax: plt.Axes, data: List[HistData]):
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

        items: List[List[HistData]] = [
            pl_data for _, pl_data in self.plots_data.items()
        ]
        assert items

        i = 0
        for y in range(self.cols):
            for x in range(self.rows):
                if i < len(items):
                    try:
                        self.histogram(axes[x, y], items[i])
                    except IndexError:
                        self.histogram(axes[x], items[i])
                    i += 1
                else:
                    self.fig.delaxes(axes[x, y])

    @overrides
    def plot(self):

        if not self.rows or not self.cols:
            # closest square
            self.cols = self.rows = int(np.ceil(np.sqrt(len(self.plots_data))))

        fig, axes = plt.subplots(ncols=self.cols, nrows=self.rows, figsize=(19, 19))
        self.fig = fig
        self.subplots(axes)
        self.fig.tight_layout()
