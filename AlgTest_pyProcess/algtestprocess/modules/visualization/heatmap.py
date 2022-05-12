import io

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


class Heatmap:
    """Class for plotting RSA most significant bytes into a heatmap"""

    def __init__(self, rsa_df, device_name):
        """
        Init function  the p,q,n bytes and builds the plot
        :param rsa_df: pandas dataframe containing the private prime an moduli
        :param device_name: to draw into the plot
        """
        self.p_byte, self.q_byte, self.n_byte = \
            Heatmap.compute_pqn_bytes(rsa_df)
        self.device_name = device_name
        self.build()

    @staticmethod
    def compute_pqn_bytes(df):
        n = list(map(lambda x: int(x, 16), list(df.n)))
        p = list(map(lambda x: int(x, 16), list(df.p)))
        q = [a // b for a, b in zip(n, p)]

        p_byte = [x >> (x.bit_length() - 8) for x in p]
        q_byte = [x >> (x.bit_length() - 8) for x in q]
        n_byte = [x >> (x.bit_length() - 8) for x in n]

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

        fig = plt.figure(figsize=(7.5, 12))

        # Outer means two main plots
        outer = gridspec.GridSpec(3, 1, height_ratios=(3, 0.5, 1))

        # Top gridspec where heatmap + hists will be
        top_gs = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=outer[0],
                                                  wspace=0, hspace=0,
                                                  width_ratios=(7, 2),
                                                  height_ratios=(2, 7))
        top_gs.left = 0.1
        top_gs.right = 0.9
        top_gs.bottom = 0.1
        top_gs.top = 0.9

        # Text gs for device name
        text_gs = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=outer[1],
                                                   wspace=0, hspace=0)

        # Bottom where small hists will be
        bottom_gs = gridspec.GridSpecFromSubplotSpec(5, 6,
                                                     subplot_spec=outer[2],
                                                     wspace=0.1, hspace=0)
        bottom_gs.left = 0.5
        bottom_gs.right = 0.5
        bottom_gs.bottom = 0.1
        bottom_gs.top = 0.9

        hm_ax = fig.add_subplot(top_gs[1, 0])
        hm_histx_ax = fig.add_subplot(top_gs[0, 0], sharex=hm_ax)
        hm_histy_ax = fig.add_subplot(top_gs[1, 1], sharey=hm_ax)

        text_ax = fig.add_subplot(text_gs[0, 0])
        text_ax.set_axis_off()
        text_ax.text(0.5, 0, device_name, transform=text_ax.transAxes,
                     ha="center", va="center", fontsize=24, color="black")

        p_dens_ax = fig.add_subplot(bottom_gs[0:2, 0:2])
        q_dens_ax = fig.add_subplot(bottom_gs[3:, 0:2])
        n_dens_ax = fig.add_subplot(bottom_gs[:, 2:8])

        cmap = LinearSegmentedColormap.from_list(
            '', Heatmap.COLORS, N=len(Heatmap.COLORS))

        # Draw heatmap/scatterplot
        hm_ax.hist2d(p_byte, q_byte, bins=range(128, 256), cmap=cmap)
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
        hm_ax.vlines(x=p_min, ymin=128, ymax=256, colors='green', ls=":", lw=2,
                     label="$P_{min}$ =" + format(p_min, 'b'))
        hm_ax.vlines(x=p_max, ymin=128, ymax=256, colors='blue', ls=":", lw=2,
                     label="$P_{max}$ =" + format(p_max, 'b'))
        hm_ax.hlines(y=q_min, xmin=128, xmax=256, colors='orange', ls=":", lw=2,
                     label="$Q_{min}$ =" + format(q_min, 'b'))
        hm_ax.hlines(y=q_max, xmin=128, xmax=256, colors='purple', ls=":", lw=2,
                     label="$Q_{max}$ =" + format(q_max, 'b'))

        hm_ax.plot(np.arange(128, 256), np.arange(128, 256), 'skyblue',
                   linestyle=':', marker='', lw=2, label="P=Q")

        # Show legend
        hm_ax.legend(loc='lower left')

        # Set the ticks in binary form
        ticks = list(range(128, 256, 8)) + [255]
        hm_ax.set_xticks(ticks)
        hm_ax.set_yticks(ticks)
        hm_ax.set_xticklabels(list(map(lambda num: format(num, "b"), ticks)),
                              rotation='vertical')
        hm_ax.set_yticklabels(list(map(lambda num: format(num, "b"), ticks)))

        # Add histograms for P and Q
        bins = np.arange(128, 256, 1)
        hm_histx_ax.hist(p_byte, bins=bins, color="black", ec="white",
                         density=True)
        hm_histy_ax.hist(q_byte, bins=bins, orientation='horizontal',
                         color="black", ec="white", density=True)

        # Turn off their axes
        hm_histx_ax.set_axis_off()
        hm_histy_ax.set_axis_off()

        # Draw p,q,n histograms
        p_dens_ax.hist(p_byte, bins=bins, color="black", histtype='stepfilled',
                       density=True)
        q_dens_ax.hist(q_byte, bins=bins, color="black", histtype='stepfilled',
                       density=True)
        n_dens_ax.hist(n_byte, bins=bins, color="black", histtype='stepfilled',
                       density=True)

        p_dens_ax.spines['top'].set_visible(False)
        p_dens_ax.spines['left'].set_visible(False)
        p_dens_ax.spines['right'].set_visible(False)
        p_dens_ax.set_xticks([128, 256])
        p_dens_ax.set_yticks([])

        q_dens_ax.spines['top'].set_visible(False)
        q_dens_ax.spines['left'].set_visible(False)
        q_dens_ax.spines['right'].set_visible(False)
        q_dens_ax.set_xticks([128, 256])
        q_dens_ax.set_yticks([])

        n_dens_ax.spines['top'].set_visible(False)
        n_dens_ax.spines['left'].set_visible(False)
        n_dens_ax.spines['right'].set_visible(False)
        n_dens_ax.set_xticks([128, 256])
        n_dens_ax.set_yticks([])

    def build(self):
        """Builds the heatmap so it can be saved or shown"""
        self.heatmap()

    def show(self):
        """Shows the heatmap"""
        plt.show()

    def svg(self):
        """Saves svg as string"""
        f = io.BytesIO()
        plt.savefig(f, format="svg")
        value = f.getvalue()
        f.close()
        return value.decode('ascii')

    def save(self, filename: str, format: str = 'png'):
        plt.savefig(filename, format=format)

    COLORS = [
        '#00000000', '#FFFFF0', '#FFFFE6', '#FFFFDB', '#FFFFD1', '#FFFFC7',
        '#FFFFBD', '#FFFFB3', '#FFFFA8', '#FFFF9E', '#FFFF94', '#FFFF8A',
        '#FFFF80', '#FFFF75', '#FFFF6B', '#FFFF61', '#FFFF57', '#FFFF4D',
        '#FFFF42', '#FFFF38', '#FFFF2E', '#FFFF24', '#FFFF19', '#FFFF0F',
        '#FFFF05', '#FFFF00', '#FFFC00', '#FFF800', '#FFF500', '#FFF100',
        '#FFEE00', '#FFEA00', '#FFE700', '#FFE300', '#FFE000', '#FFDD00',
        '#FFD900', '#FFD600', '#FFD200', '#FFCF00', '#FFCB00', '#FFC800',
        '#FFC400', '#FFC100', '#FFBE00', '#FFBA00', '#FFB700', '#FFB300',
        '#FFB000', '#FFAC00', '#FFA900', '#FFA500', '#FFA200', '#FF9F00',
        '#FF9B00', '#FF9800', '#FF9400', '#FF9100', '#FF8D00', '#FF8A00',
        '#FF8600', '#FF8300', '#FF8000', '#FF7C00', '#FF7900', '#FF7500',
        '#FF7200', '#FF6E00', '#FF6B00', '#FF6700', '#FF6400', '#FF6000',
        '#FF5D00', '#FF5A00', '#FF5600', '#FF5300', '#FF4F00', '#FF4C00',
        '#FF4800', '#FF4500', '#FF4100', '#FF3E00', '#FF3B00', '#FF3700',
        '#FF3400', '#FF3000', '#FF2D00', '#FF2900', '#FF2600', '#FF2200',
        '#FF1F00', '#FF1C00', '#FF1800', '#FF1500', '#FF1100', '#FF0E00',
        '#FF0A00', '#FF0700', '#FF0300', '#FF0000']

