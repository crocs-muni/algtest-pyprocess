import sys
from typing import List, Optional

import click
from click import Path

from algtestprocess.modules.jcalgtest import (
    ProfilePerformanceFixedJC, ProfileSupportJC, ProfilePerformanceVariableJC
)
from algtestprocess.modules.pages.comparativetable import ComparativeTable
from algtestprocess.modules.pages.executiontime import ExecutionTime
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.radar import Radar
from algtestprocess.modules.pages.scalability import Scalability
from algtestprocess.modules.pages.similarity import Similarity
from algtestprocess.modules.pages.support import Support
from algtestprocess.modules.parser.javacard.performance import \
    PerformanceParser, create_sorted_already_measured_list, fix_error_codes, \
    fix_missing_underscores, fix_missing_variable_data_lengths, convert_to_json, \
    prepare_missing_measurements, compute_stats, get_files_to_process
from algtestprocess.modules.parser.javacard.support import SupportParser


def fix_results(directory):
    all_to_measure_ops = create_sorted_already_measured_list(directory)
    # error codes not translated into human readable string _
    fix_error_codes(directory)
    # some file had incorrect naming for measured values without _
    fix_missing_underscores(directory, all_to_measure_ops)
    fix_missing_variable_data_lengths(directory)


def process_results(directory: str):
    fix_results(directory)
    # from csv to json (dict)
    convert_to_json(directory, True)
    # prepare *__already_measured.list files to collect missing measurements
    prepare_missing_measurements(directory)
    compute_stats(directory)


def get_profiles(directory):
    performance_dir = f"{directory}/javacard/Profiles/performance/"
    support_dir = f"{directory}/javacard/Profiles/results/"
    files = get_files_to_process(performance_dir, ".json")
    profiles_fixed = list(map(
        lambda x: PerformanceParser(x).parse(ProfilePerformanceFixedJC()),
        filter(lambda x: "fixed" in x, files)))
    profiles_variable = list(map(
        lambda x: PerformanceParser(x).parse(ProfilePerformanceVariableJC()),
        filter(lambda x: "variable" in x, files)))
    profiles_support = list(map(
        lambda x: SupportParser(x).parse(ProfileSupportJC()),
        get_files_to_process(support_dir, ".csv")))
    return profiles_fixed, profiles_variable, profiles_support


def run(to_run: List[Page], output_dir: str):
    for runner in to_run:
        runner.run(output_dir)


@click.command()
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
        "support"
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
    default=None,
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="Path to folder where you want output to be stored."
)
def main(
        operations: List[str],
        results_dir: Optional[Path],
        output_dir: Optional[Path]
):
    if not results_dir and not output_dir:
        print("results-dir nor output_dir was specified")
        sys.exit(1)

    if "process" in operations and results_dir:
        process_results(f"{results_dir}/javacard/Profiles/performance/")

    operations = {
        "execution-time",
        "comparative",
        "radar",
        "scalability",
        "similarity",
        "support"
    } if "all" in operations else set(operations)

    fixed, variable, support = get_profiles(results_dir)
    to_run = []

    if "execution" in operations:
        to_run.append(ExecutionTime(fixed))

    if "comparative" in operations:
        to_run.append(ComparativeTable(fixed))

    if "radar" in operations:
        to_run.append(Radar(fixed))

    if "scalability" in operations:
        to_run.append(Scalability(variable))

    if "similarity" in operations:
        to_run.append(Similarity(fixed))

    if "support" in operations:
        to_run.append(Support(support))

    if output_dir:
        run(to_run, output_dir)


if __name__ == "__main__":
    main()
