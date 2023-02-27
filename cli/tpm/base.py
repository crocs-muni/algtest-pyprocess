import click

from cli.tpm.commands.misc.summary import summary, summary_export
from cli.tpm.commands.plot.heatmaps import heatmaps_single, heatmaps_grouped
from cli.tpm.commands.plot.spectrograms import spectrograms_single, \
    spectrograms_grouped


@click.group(
    name='tpm',
    help='A collection of commands for processing of results from tpm2-algtest',
)
def tpm_cli():
    pass


@tpm_cli.group(help='Plot various visualisations from given data')
def plot():
    pass


plot.add_command(spectrograms_single)
plot.add_command(spectrograms_grouped)
plot.add_command(heatmaps_single)
plot.add_command(heatmaps_grouped)


@tpm_cli.group(help='Create outputs such as summary table and other '
                    'miscellaneous stuff')
def misc():
    pass

misc.add_command(summary_update)
misc.add_command(summary_export)


@tpm_cli.group(help='Create static HTML files from given data')
def pages():
    pass
