import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import logging
import numpy as np
import seaborn as sns
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from overrides import overrides

from algtestprocess.modules.visualization.plot import Plot


class Heatmap(Plot):
    """Class for plotting RSA most significant bytes into a heatmap"""

    DEFAULT_PARTS = {"heatmap", "text", "distributions"}

    def __init__(
        self,
        rsa_df,
        device_name,
        pqnf=None,
        title="",
        fig=None,
        ticks=True,
        legend=True,
        parts=DEFAULT_PARTS,
        part_height_ratios=(3, 0.5, 1),
        verbose=False,
        text_font_size=12,
        title_font_size=24,
        label_values=True,
        additional_text=None,
        additional_text_font_size=5,
    ):
        """
        Init function  the p,q,n bytes and builds the plot
        :param rsa_df: pandas dataframe containing the private prime an moduli
        :param device_name: to draw into the plot
        :param pqnf: possibly a function which takes df as input and returns the PQN MSBs
        :param title: text, possibly short abbreviation for the host computer
        """
        super().__init__()
        pqnf = pqnf or self.compute_pqn_bytes
        print(device_name, len(rsa_df))
        self.device_name = device_name
        self.title = title
        self.p_byte, self.q_byte, self.n_byte = pqnf(rsa_df)
        self.fig = fig
        self.ticks = ticks
        self.legend = legend
        self.parts = set(parts) if not isinstance(parts, set) else parts
        self.part_height_ratios = part_height_ratios
        self.verbose = verbose
        self.text_font_size = text_font_size
        self.title_font_size = title_font_size
        self.label_values = label_values
        self.additional_text = additional_text
        self.additional_text_font_size = additional_text_font_size

    def compute_pqn_bytes(self, df):
        df = df.dropna(subset=["p", "q", "n"])

        if len(df) < 1:
            raise ValueError("visualized dataframe must not be empty")

        # As the data doesn't contain q prime it needs to be computed
        n = list(map(lambda x: int(x, 16), list(df.n)))
        p = list(map(lambda x: int(x, 16), list(df.p)))
        q = [a // b for a, b in zip(n, p)]

        p_byte = [
            x
            >> (x.bit_length() - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8))
            for x in p
        ]
        q_byte = [
            x
            >> (x.bit_length() - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8))
            for x in q
        ]
        n_byte = [
            x
            >> (x.bit_length() - (8 if x.bit_length() % 8 == 0 else x.bit_length() % 8))
            for x in n
        ]

        return p_byte, q_byte, n_byte

    def heatmap(self):
        device_name = self.device_name
        p_byte = self.p_byte
        q_byte = self.q_byte
        n_byte = self.n_byte

        record_count = len(p_byte)
        p_min = min(p_byte)
        p_max = max(p_byte)
        q_min = min(q_byte)
        q_max = max(q_byte)
        n_min = min(n_byte)
        n_max = max(n_byte)

        fig = self.fig
        if fig is None:
            fig = plt.figure(figsize=(7.5, 12))
            self.fig = fig

        if "title" in self.parts:
            fig.suptitle(
                self.title, fontsize=self.title_font_size, ha="right", va="top"
            )

        # Now we create a number of rows based on desired parts
        nrows = len(self.parts & Heatmap.DEFAULT_PARTS)
        if self.verbose:
            print(f"Plot will have {nrows=}")
        outer = gridspec.GridSpec(nrows, 1, height_ratios=self.part_height_ratios)

        # Top gridspec where heatmap + hists will be
        top_gs = gridspec.GridSpecFromSubplotSpec(
            2,
            2,
            subplot_spec=outer[0],
            wspace=0,
            hspace=0,
            width_ratios=(7, 2),
            height_ratios=(2, 7),
        )
        # top_gs.left = 0.1
        # top_gs.right = 0.9
        # top_gs.bottom = 0.1
        # top_gs.top = 0.9

        if "text" in self.parts:
            # Text gs for device name
            text_gs = gridspec.GridSpecFromSubplotSpec(
                1 if self.additional_text is None else 4,
                1,
                subplot_spec=outer[1],
                wspace=0,
                hspace=0,
            )
            text_gs.top = 0.9

        if "distributions" in self.parts:
            # Bottom where small hists will be
            bottom_gs = gridspec.GridSpecFromSubplotSpec(
                5, 6, subplot_spec=outer[2], wspace=0.1, hspace=0
            )
            bottom_gs.left = 0.5
            bottom_gs.right = 0.5
            bottom_gs.bottom = 0.1
            bottom_gs.top = 0.9

        if "heatmap" in self.parts:
            hm_ax = fig.add_subplot(top_gs[1, 0])
            hm_histx_ax = fig.add_subplot(top_gs[0, 0], sharex=hm_ax)
            hm_histy_ax = fig.add_subplot(top_gs[1, 1], sharey=hm_ax)

        if "text" in self.parts:
            text_ax = fig.add_subplot(
                text_gs[0, 0] if self.additional_text is None else text_gs[1, 0]
            )
            text_ax.set_axis_off()
            text_ax.text(
                0.4,
                -5 if self.additional_text is not None else -1.2,
                device_name,
                transform=text_ax.transAxes,
                ha="center",
                va="top",
                fontsize=self.text_font_size,
                color="black",
                fontfamily="serif",
            )

            if self.additional_text is not None:
                additional_text_ax = fig.add_subplot(text_gs[2:, 0])
                additional_text_ax.set_axis_off()
                additional_text_ax.text(
                    0,
                    -5,
                    self.additional_text,
                    transform=additional_text_ax.transAxes,
                    ha="left",
                    va="center",
                    fontsize=self.additional_text_font_size,
                    color="black",
                    fontweight="regular",
                    fontfamily="serif",
                    zorder=10000,
                )

        if "distributions" in self.parts:
            p_dens_ax = fig.add_subplot(bottom_gs[0:2, 0:2])
            q_dens_ax = fig.add_subplot(bottom_gs[3:, 0:2])
            n_dens_ax = fig.add_subplot(bottom_gs[:, 2:8])

        # Draw heatmap/scatterplot
        if "heatmap" in self.parts:
            cmap = LinearSegmentedColormap.from_list(
                "Random gradient 9291",
                (
                    # Edit this gradient at https://eltos.github.io/gradient/#Random%20gradient%209291=25:D35248-50:E2453B-75:BA0700-100:710000
                    (0.000, (0.827, 0.322, 0.282)),
                    (0.250, (0.827, 0.322, 0.282)),
                    (0.500, (0.886, 0.271, 0.231)),
                    (0.750, (0.729, 0.027, 0.000)),
                    (1.000, (0.443, 0.000, 0.000)),
                ),
            )
            cmap.set_bad("#FFFFFF")
            sns.histplot(
                x=p_byte, y=q_byte, bins=range(128, 256), ax=hm_ax, cmap=cmap, vmin=1
            )

            hm_ax.set_xlim(128, 255)
            hm_ax.set_ylim(128, 255)
            hm_ax.set_xlabel("P", loc="left")
            hm_ax.set_ylabel("Q", loc="bottom")

            # Position label for P (xaxis)
            xlbl = hm_ax.xaxis.get_label()
            x0, y0 = xlbl.get_position()
            hm_ax.xaxis.set_label_coords(x0 - 0.1, y0 - 0.175)

            # Position label for Q (yaxis)
            ylbl = hm_ax.yaxis.get_label()
            x0, y0 = ylbl.get_position()
            hm_ax.yaxis.set_label_coords(x0 - 0.1, y0 - 0.1)

            # Colored vertical lines for maximums and minimums
            hm_ax.vlines(
                x=p_min,
                ymin=128,
                ymax=256,
                colors="green",
                ls=":",
                lw=1,
                label="$P_{min}$"
                + (" =" + format(p_min, "b") if self.label_values else ""),
            )
            hm_ax.vlines(
                x=p_max,
                ymin=128,
                ymax=256,
                colors="blue",
                ls=":",
                lw=1,
                label="$P_{max}$"
                + (" =" + format(p_max, "b") if self.label_values else ""),
            )
            hm_ax.hlines(
                y=q_min,
                xmin=128,
                xmax=256,
                colors="orange",
                ls=":",
                lw=1,
                label="$Q_{min}$"
                + (" =" + format(q_min, "b") if self.label_values else ""),
            )
            hm_ax.hlines(
                y=q_max,
                xmin=128,
                xmax=256,
                colors="purple",
                ls=":",
                lw=1,
                label="$Q_{max}$"
                + (" =" + format(q_max, "b") if self.label_values else ""),
            )

            hm_ax.plot(
                list(range(128, 256)),
                list(range(128, 256)),
                "black",
                linestyle=":",
                marker="",
                lw=1,
                label="P=Q",
            )

        # Show legend
        if self.legend:
            hm_ax.legend(loc="lower left")

        if self.ticks:
            # Set the ticks in binary form
            ticks = list(range(128, 256, 8)) + [255]
            hm_ax.set_xticks(ticks)
            hm_ax.set_yticks(ticks)
            hm_ax.set_xticklabels(
                list(map(lambda num: format(num, "b"), ticks)), rotation="vertical"
            )
            hm_ax.set_yticklabels(list(map(lambda num: format(num, "b"), ticks)))
            hm_ax.set_aspect("equal", adjustable="box")

        if "heatmap" in self.parts:
            # Add histograms for P and Q
            bins = list(range(128, 257, 1))
            hm_histx_ax.hist(p_byte, bins=bins, color="white", ec="black", density=True)
            hm_histy_ax.hist(
                q_byte,
                bins=bins,
                orientation="horizontal",
                color="white",
                ec="black",
                density=True,
            )

            # Turn off their axes
            hm_histx_ax.set_axis_off()
            hm_histy_ax.set_axis_off()

        if "distributions" in self.parts:
            # Draw p,q,n histograms
            p_dens_ax.hist(
                p_byte, bins=bins, color="black", histtype="stepfilled", density=True
            )
            q_dens_ax.hist(
                q_byte, bins=bins, color="black", histtype="stepfilled", density=True
            )
            n_dens_ax.hist(
                n_byte, bins=bins, color="black", histtype="stepfilled", density=True
            )

            p_dens_ax.spines["top"].set_visible(False)
            p_dens_ax.spines["left"].set_visible(False)
            p_dens_ax.spines["right"].set_visible(False)
            p_dens_ax.set_xticks([128, 256])
            p_dens_ax.set_yticks([])

            q_dens_ax.spines["top"].set_visible(False)
            q_dens_ax.spines["left"].set_visible(False)
            q_dens_ax.spines["right"].set_visible(False)
            q_dens_ax.set_xticks([128, 256])
            q_dens_ax.set_yticks([])

            n_dens_ax.spines["top"].set_visible(False)
            n_dens_ax.spines["left"].set_visible(False)
            n_dens_ax.spines["right"].set_visible(False)
            n_dens_ax.set_xticks([128, 256])
            n_dens_ax.set_yticks([])

    @overrides
    def plot(self):
        self.heatmap()

    # This was copypasted from R, no way im gonna compute the sequence
    COLORS = [
        "#D3D3D3",
        "#FFFFF0",
        "#FFFFE6",
        "#FFFFDB",
        "#FFFFD1",
        "#FFFFC7",
        "#FFFFBD",
        "#FFFFB3",
        "#FFFFA8",
        "#FFFF9E",
        "#FFFF94",
        "#FFFF8A",
        "#FFFF80",
        "#FFFF75",
        "#FFFF6B",
        "#FFFF61",
        "#FFFF57",
        "#FFFF4D",
        "#FFFF42",
        "#FFFF38",
        "#FFFF2E",
        "#FFFF24",
        "#FFFF19",
        "#FFFF0F",
        "#FFFF05",
        "#FFFF00",
        "#FFFC00",
        "#FFF800",
        "#FFF500",
        "#FFF100",
        "#FFEE00",
        "#FFEA00",
        "#FFE700",
        "#FFE300",
        "#FFE000",
        "#FFDD00",
        "#FFD900",
        "#FFD600",
        "#FFD200",
        "#FFCF00",
        "#FFCB00",
        "#FFC800",
        "#FFC400",
        "#FFC100",
        "#FFBE00",
        "#FFBA00",
        "#FFB700",
        "#FFB300",
        "#FFB000",
        "#FFAC00",
        "#FFA900",
        "#FFA500",
        "#FFA200",
        "#FF9F00",
        "#FF9B00",
        "#FF9800",
        "#FF9400",
        "#FF9100",
        "#FF8D00",
        "#FF8A00",
        "#FF8600",
        "#FF8300",
        "#FF8000",
        "#FF7C00",
        "#FF7900",
        "#FF7500",
        "#FF7200",
        "#FF6E00",
        "#FF6B00",
        "#FF6700",
        "#FF6400",
        "#FF6000",
        "#FF5D00",
        "#FF5A00",
        "#FF5600",
        "#FF5300",
        "#FF4F00",
        "#FF4C00",
        "#FF4800",
        "#FF4500",
        "#FF4100",
        "#FF3E00",
        "#FF3B00",
        "#FF3700",
        "#FF3400",
        "#FF3000",
        "#FF2D00",
        "#FF2900",
        "#FF2600",
        "#FF2200",
        "#FF1F00",
        "#FF1C00",
        "#FF1800",
        "#FF1500",
        "#FF1100",
        "#FF0E00",
        "#FF0A00",
        "#FF0700",
        "#FF0300",
        "#FF0000",
    ]
