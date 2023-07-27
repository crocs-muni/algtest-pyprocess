import click

from algtestprocess.modules.cli.tpm.commands.metadata_update import \
    metadata_update
from algtestprocess.modules.cli.tpm.commands.report_create import report_create
from algtestprocess.modules.cli.tpm.commands.summary_create import \
    summary_create


@click.group(
    name='tpm',
    help='A collection of commands for processing of results from tpm2-algtest',
)
def tpm_cli():
    pass


tpm_cli.add_command(metadata_update)
tpm_cli.add_command(report_create)
tpm_cli.add_command(summary_create)
