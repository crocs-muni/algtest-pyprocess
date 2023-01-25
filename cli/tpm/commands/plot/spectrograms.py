import click


@click.command()
@click.argument(
    'root_path',
    type=click.Path(exists=True, dir_okay=True)
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True)
)
def spectrograms_single(root_path):
    """
    Creates spectrogram plots for single measurement

    ROOT_PATH is tpm2-algtest measurement folder root directory path,
    also known as the folder which has the following structure:

    \b
    . is the ROOT_PATH
    ./detail/ is REQUIRED folder
    ./performance.yaml
    ./results.yaml

    """
    pass


@click.command()
@click.argument(
    'measurements_path',
    type=click.Path(exists=True, dir_okay=True)
)
@click.argument(
    "group_by",
    required=True,
    nargs=1,
    type=click.Choice(["HOST", "TPM"], case_sensitive=True)
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(dir_okay=True, file_okay=False, writable=True)
)
def spectrograms_grouped(measurements_path, group_by, output_path):
    """
    Creates spectrogram plots for multiple measurements grouped by either
    HOST computer, or TPM device id.

    MEASUREMENTS_FOLDER is a directory path containing tpm2-algtest
    measurement folders. There CANNOT be any intermediate folders.
    """
    pass
