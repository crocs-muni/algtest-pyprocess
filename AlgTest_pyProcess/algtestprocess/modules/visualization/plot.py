import io
from abc import ABC, abstractmethod
from typing import Optional
import matplotlib.pyplot as plt


class Plot(ABC):
    def __init__(self):
        self.fig: Optional[plt.Figure] = None

    @abstractmethod
    def plot(self):
        """Abstract method which is called by build()"""
        pass

    def build(self):
        """Builds the plot so it can be saved or shown"""
        self.plot()
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
        return value.decode("ascii")

    def save(self, filename: str, format: str = "png"):
        """Saves the figure in under the given filename and in given format"""
        plt.savefig(filename, format=format)
        self.finalize()

    def finalize(self):
        plt.close(self.fig)
        self.fig = None
