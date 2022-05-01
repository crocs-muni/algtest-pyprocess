from typing import Tuple, List

import numpy as np
import matplotlib.pyplot as plt


def heatmap(
        x: List[int],
        y: List[int],
        output_path: str,
        name: str
):
    plt.hist2d(x, y, bins=(np.arange(128, 256, 8), np.arange(128, 256, 8)))

    output_path = f"{output_path}/{name}.svg"
    plt.savefig(output_path, format="svg")
