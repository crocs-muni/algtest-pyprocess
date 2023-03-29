import click


@click.command
def report_update():
    """
    Over several steps collects metadata on what is to be included in the report,
    preventing things such as double includes and similar.
    """
    pass


@click.command
def report_create():
    """
    Creates several folders and files, containing various info. Assumes we are
    content with all the folders we set up to be included in the report.

    Each path is relative to OUTPUT_PATH given as an argument

    ./tpms/summary.{md/html}                                # Collected TPMs summary file
    ./tpms/VENDOR_NAME/summary.{md/html}                    # Vendor summary file
    ./tpms/VENDOR_NAME/[TPM_NAME]/{*.png, summary.{md/html} # TPM summary file and visualisations
    """
    pass