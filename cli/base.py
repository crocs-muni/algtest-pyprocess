import logging

logging.basicConfig(
    filename="pyprocess_log.txt",
    encoding='utf-8',
    level=logging.DEBUG
)

import click

from cli.tpm.base import tpm_cli


@click.group()
def cli():
    pass


cli.add_command(tpm_cli)
