import matplotlib.pyplot as plt
import numpy as np
import io
import matplotlib.gridspec as gridspec


class Heatmap:

    def __init__(self, rsa_df, device_name):
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
        n_byte = self.q_byte
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

        # Draw heatmap/scatterplot
        hm_ax.hist2d(p_byte, q_byte, bins=(128, 128), cmap=plt.cm.Oranges)
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
        hm_histx_ax.hist(p_byte, bins=bins, color="black", ec="white")
        hm_histy_ax.hist(q_byte, bins=bins, orientation='horizontal',
                         color="black", ec="white")

        # Turn off their axes
        hm_histx_ax.set_axis_off()
        hm_histy_ax.set_axis_off()

        # Draw p,q,n histograms
        p_dens_ax.hist(p_byte, bins=bins, color="black", histtype='stepfilled')
        q_dens_ax.hist(q_byte, bins=bins, color="black", histtype='stepfilled')
        n_dens_ax.hist(q_byte, bins=bins, color="black", histtype='stepfilled')

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


