import json
import os
import sys
from typing import List, Optional

import click
from click import Path

from algtestprocess.modules.pages.comparativetable import ComparativeTable
from algtestprocess.modules.pages.compare import CompareJC, CompareTPM
from algtestprocess.modules.pages.executiontime import ExecutionTimeJC, \
    ExecutionTimeTPM
from algtestprocess.modules.pages.heatmaps import Heatmaps
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.radar import RadarJC, RadarTPM
from algtestprocess.modules.pages.scalability import Scalability
from algtestprocess.modules.pages.similarity import SimilarityJC, SimilarityTPM
from algtestprocess.modules.pages.support import SupportJC, SupportTPM
from algtestprocess.modules.parser.getters import get_javacard_profiles, \
    get_tpm_profiles


def run(to_run: List[Page], output_dir: str):
    for runner in to_run:
        runner.run(output_dir)


@click.command()
@click.argument(
    "devices",
    required=True,
    nargs=1,
    type=click.Choice([
        "javacard",
        "tpm"
    ], case_sensitive=False)
)
@click.argument(
    "operations",
    required=True,
    nargs=-1,
    type=click.Choice([
        "process",
        "all",
        "execution-time",
        "comparative",
        "radar",
        "scalability",
        "similarity",
        "support",
        "compare",
        "heatmap",
        "export"
    ], case_sensitive=False
    )
)
@click.option(
    "-i",
    "--results-dir",
    "results_dir",
    default=None,
    type=click.Path(file_okay=False, dir_okay=True, readable=True),
    help="Path to folder with results root directory."
)
@click.option(
    "-o",
    "--output-dir",
    "output_dir",
    default=".",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="Path to folder where you want output to be stored."
)
def main(
        devices: List[str],
        operations: List[str],
        results_dir: Optional[Path],
        output_dir: Optional[Path]
):
    if not results_dir:
        print("results-dir was NOT specified")
        sys.exit(1)

    fixed = variable = support = performance = support_tpm = cryptoprops = []

    if "javacard" in devices:
        fixed, variable, support = get_javacard_profiles(
            results_dir,
            preprocess="process" in operations
        )

    if "tpm" in devices:
        performance, support_tpm, cryptoprops = get_tpm_profiles(results_dir)

    operations = {
        "execution-time",
        "comparative",
        "radar",
        "scalability",
        "similarity",
        "support",
        "compare",
        "heatmap",
    } if "all" in operations else set(operations)

    to_run = []

    if "execution-time" in operations:
        if "javacard" in devices:
            to_run.append(ExecutionTimeJC(fixed))
        if "tpm" in devices:
            to_run.append(ExecutionTimeTPM(performance))

    if "comparative" in operations:
        if "javacard" in devices:
            to_run.append(ComparativeTable(fixed))

    if "radar" in operations:
        if "javacard" in devices:
            to_run.append(RadarJC(fixed))
        if "tpm" in devices:
            to_run.append(RadarTPM(performance))

    if "scalability" in operations:
        if "javacard" in devices:
            to_run.append(Scalability(variable))

    if "similarity" in operations:
        if "javacard" in devices:
            to_run.append(SimilarityJC(fixed))
        if "tpm" in devices:
            to_run.append(SimilarityTPM(performance))

    if "support" in operations:
        if "javacard" in devices:
            to_run.append(SupportJC(support))
        if "tpm" in devices:
            to_run.append(SupportTPM(support_tpm))

    if "compare" in operations:
        if "javacard" in devices:
            to_run.append(CompareJC(fixed))
        if "tpm" in devices:
            to_run.append(CompareTPM(performance))

    if "heatmap" in operations:
        if "tpm" in devices:
            to_run.append(Heatmaps(cryptoprops))

    if "export" in operations:
        to_export = []
        if "javacard" in devices:
            to_export += [
                ("javacard_performance_fixed.json", fixed) if fixed else None,
                ("javacard_performance_variable.json", variable) if variable else None,
                ("javacard_support.json", support) if support else None
            ]
        if "tpm" in devices:
            to_export += [
                ("tpm_performance.json", performance) if performance else None,
                ("tpm_support.json", support_tpm) if support_tpm else None
            ]
        for item in to_export:
            if not item:
                continue

            filename, profiles = item
            with open(f"{output_dir}/{filename}", "w", encoding='utf-8') as f:
                data = [profile.export() for profile in profiles]
                json.dump(data, f, ensure_ascii=False, indent=4)

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    run(to_run, output_dir)


if __name__ == "__main__":
    main()
