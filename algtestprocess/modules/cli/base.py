import logging

logging.basicConfig(
    filename="pyprocess_log.txt",
    encoding='utf-8',
    level=logging.INFO,
    filemode='a'
)

import click

from algtestprocess.modules.cli.tpm.base import tpm_cli


@click.group()
def cli():
    pass


cli.add_command(tpm_cli)
