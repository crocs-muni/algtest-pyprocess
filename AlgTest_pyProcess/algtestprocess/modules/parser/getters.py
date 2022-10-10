import os
import re
import sys

from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC, \
    ProfilePerformanceVariableJC
from algtestprocess.modules.parser.javacard.performance import \
    get_files_to_process, PerformanceParserJC, \
    create_sorted_already_measured_list, fix_error_codes, \
    fix_missing_underscores, fix_missing_variable_data_lengths, convert_to_json, \
    prepare_missing_measurements, compute_stats
from algtestprocess.modules.parser.javacard.support import SupportParserJC
from algtestprocess.modules.parser.tpm.cryptoprops import CryptoProps
from algtestprocess.modules.parser.tpm.performance import PerformanceParserTPM
from algtestprocess.modules.parser.tpm.support import SupportParserTPM


def get_javacard_profiles(directory, preprocess: bool):
    """
        When parsing profiles for JavaCards, it is assumed that fixed and variable
        results were processed before and *.json outputs were created. That means
        script was called with `process` argument.

        Following path illustrate valid result directories

        Performance results folder with *.json files
        {directory}/.*/[Pp]erformance/(fixed|variable)/

        Support results folder with *.csv files
        {directory}/.*/[rR]esults/

    """

    perf_dir = [
        os.path.join(root, dirname)
        for root, dirnames, _ in os.walk(directory)
        for dirname in dirnames if dirname.lower() == 'performance'
    ]

    if preprocess:
        # Need performance dir to process the perf profiles
        assert perf_dir
        process_results(f"{perf_dir[0]}/")

    files_performance = get_files_to_process(directory, ".json")

    if not files_performance:
        print("get_javacard_profiles:"
              " script needs to be called with process argument first")
        sys.exit(1)

    files_support = get_files_to_process(directory, ".csv")

    profiles_fixed = list(map(
        lambda x: PerformanceParserJC(x).parse(ProfilePerformanceFixedJC()),
        filter(
            lambda y: "/performance/" in y.lower() and "/fixed/" in y,
            files_performance
        )))
    rename_duplicates(profiles_fixed)
    profiles_variable = list(map(
        lambda x: PerformanceParserJC(x).parse(ProfilePerformanceVariableJC()),
        filter(
            lambda y: "/performance/" in y.lower() and "/variable/" in y,
            files_performance
        )))
    rename_duplicates(profiles_variable)
    profiles_variable = sorted(profiles_variable, key=lambda x: x.device_name().lower())

    profiles_support = list(map(
        lambda x: SupportParserJC(x).parse(),
        filter(
            lambda y: "/results/" in y.lower(),
            files_support
        )))
    rename_duplicates(profiles_support)
    profiles_support = sorted(profiles_support, key=lambda x: x.device_name().lower())

    return profiles_fixed, profiles_variable, profiles_support


def get_tpm_profiles(directory, legacy):
    """
       When parsing tpm profiles

       IMPORTANT: Legacy profiles <= 10/2022
       For performance profiles folder with *.csv results
       {directory}/.*/[Pp]erformance/

       For support profiles folder with *.csv results
       {directory}/.*/[Rr]esults/

       For cryptographic properties folder with *.csv results
       {directory}/.*/[Dd]etail/
    """
    files = [
        os.path.join(root, file)
        for root, _, files in os.walk(directory) for file in files
    ]

    perf_parser = lambda path: PerformanceParserTPM(path).parse()
    perf_name = lambda name: "performance.txt" in name.lower()
    if legacy:
        perf_parser = lambda path: PerformanceParserTPM(path).parse_legacy()
        perf_name = lambda name: "/performance/" in name.lower() and ".csv" in name

    performance = list(filter(perf_name, files))
    performance = list(filter(
        lambda profile: profile.results, map(perf_parser, performance)
    ))
    rename_duplicates(performance)
    performance = sorted(performance, key=lambda x: x.device_name().lower())

    support_parser = lambda path: SupportParserTPM(path).parse()
    support_name = lambda name: "results.txt" in name
    if legacy:
        support_parser = lambda path: SupportParserTPM(path).parse_legacy()
        support_name = lambda name: "/results/" in name.lower() and ".csv" in name

    support = list(filter(support_name, files))
    support = list(filter(
        lambda profile: profile.results, map(support_parser, support)
    ))
    rename_duplicates(support)
    support = sorted(
        support, key=lambda x: (x.device_name().lower())
    )

    cryptoprops_paths = list(set(
        map(lambda match: match.group(1),
            filter(None, map(lambda name: re.search(r'(.*/[Dd]etail/).*', name),
                             files)))
    ))
    cryptoprops = list(filter(None, map(lambda path: CryptoProps(path).parse(),
                                        cryptoprops_paths)))

    return performance, support, cryptoprops


def rename_duplicates(profiles):
    """Renames the profiles with same name"""
    for profile in profiles:
        duplicates = list(filter(
            lambda x: x.device_name() == profile.device_name(),
            profiles
        ))
        if len(duplicates) > 1:
            for i, dupe in enumerate(duplicates):
                dupe.rename(f"{dupe.device_name()} [{i + 1}]")


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
