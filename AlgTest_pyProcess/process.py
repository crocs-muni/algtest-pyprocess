import os
import sys
from typing import List, Optional

import click
from click import Path

from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC, ProfilePerformanceVariableJC

from algtestprocess.modules.pages.comparativetable import ComparativeTable
from algtestprocess.modules.pages.compare import Compare
from algtestprocess.modules.pages.executiontime import ExecutionTimeJC, \
    ExecutionTimeTPM
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.radar import RadarJC, RadarTPM
from algtestprocess.modules.pages.scalability import Scalability
from algtestprocess.modules.pages.similarity import SimilarityJC, SimilarityTPM
from algtestprocess.modules.pages.support import SupportJC, SupportTPM
from algtestprocess.modules.parser.javacard.performance import \
    PerformanceParserJC, create_sorted_already_measured_list, fix_error_codes, \
    fix_missing_underscores, fix_missing_variable_data_lengths, convert_to_json, \
    prepare_missing_measurements, compute_stats, get_files_to_process
from algtestprocess.modules.parser.javacard.support import SupportParserJC
from algtestprocess.modules.parser.tpm.detail import Detail
from algtestprocess.modules.parser.tpm.performance import PerformanceParserTPM
from algtestprocess.modules.parser.tpm.support import SupportParserTPM
from algtestprocess.modules.visualisation.heatmap import heatmap


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


def get_javacard_profiles(directory):
    performance_dir = f"{directory}/javacard/Profiles/performance/"
    support_dir = f"{directory}/javacard/Profiles/results/"
    files_performance = get_files_to_process(performance_dir, ".json")
    files_support = get_files_to_process(support_dir, ".csv")
    profiles_fixed = list(map(
        lambda x: PerformanceParserJC(x).parse(ProfilePerformanceFixedJC()),
        filter(lambda x: "fixed" in x, files_performance)))
    profiles_variable = list(map(
        lambda x: PerformanceParserJC(x).parse(ProfilePerformanceVariableJC()),
        filter(lambda x: "variable" in x, files_performance)))
    profiles_support = list(map(
        lambda x: SupportParserJC(x).parse(), files_support))
    return profiles_fixed, profiles_variable, profiles_support


def get_tpm_profiles(directory):
    files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(directory) for file in files]
    performance = list(filter(
        lambda name: "/performance/" in name and ".csv" in name, files))
    performance = list(filter(
        lambda profile: profile.results,
        map(lambda path: PerformanceParserTPM(path).parse(), performance)))
    support = list(filter(
        lambda name: "/results/" in name and ".csv" in name, files))
    support = list(filter(
        lambda profile: profile.results,
        map(lambda path: SupportParserTPM(path).parse(), support)))
    return performance, support


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
        "heatmap"
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
        devices: List[str],
        operations: List[str],
        results_dir: Optional[Path],
        output_dir: Optional[Path]
):
    if not results_dir and not output_dir:
        print("results-dir nor output_dir was specified")
        sys.exit(1)

    if "javacard" in devices and "process" in operations and results_dir:
        # Results are fixed, generates json results, unmeasured operations
        # from .csv files. Time consuming operation, needs to be run only
        # once so that json data is generated for further use
        process_results(f"{results_dir}/javacard/Profiles/performance/")

    operations = {
        "execution-time",
        "comparative",
        "radar",
        "scalability",
        "similarity",
        "support",
        "compare"
        "heatmap"
    } if "all" in operations else set(operations)

    if "javacard" in devices:
        fixed, variable, support = get_javacard_profiles(results_dir)

    if "tpm" in devices:
        performance, support_tpm = get_tpm_profiles(results_dir)

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
            to_run.append(Compare(fixed))


    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)


    run(to_run, output_dir)


if __name__ == "__main__":
    main()
