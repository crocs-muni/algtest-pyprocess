import click

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


@tpm_cli.group(help='Create static HTML files from given data')
def pages():
    pass
