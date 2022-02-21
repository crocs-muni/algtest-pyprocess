from abc import ABC, abstractmethod
from functools import partial
from typing import List, Dict, Callable, Optional

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.cardlist import cardlist
from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.simpletable import simple_table
from algtestprocess.modules.jcalgtest import (
    ProfilePerformanceFixedJC,
    MeasurementCategory,
)
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.utils import run_helper
from algtestprocess.modules.tpmalgtest import ProfilePerformanceTPM

Profile = ProfilePerformanceFixedJC | ProfilePerformanceTPM


class ExecutionTime(ABC):

    @staticmethod
    def quick_links(categories: List[str]):
        tags.h3("Quick links")
        with tags.div(className="list-group"):
            for category in categories:
                tags.a(
                    category,
                    href=f"#{category}",
                    className="list-group-item list-group-item-action"
                )

    @staticmethod
    def dict_table(
            name: str,
            dictionary: Dict[str, str]
    ):
        tags.h3(name)
        data = [
            [key, val]
            for key, val in dictionary.items()]
        simple_table(data)

    @staticmethod
    def intro(
            profile: Profile,
            categories: List[str],
            heading: Callable,
            middle_additions: Optional[Callable] = None,
            right_additions: Optional[Callable] = None):
        with tags.div(className="row pt-5"):
            heading(profile)

            with tags.div(className="col-md-3 col-xs-3"):
                ExecutionTime.quick_links(categories)

            with tags.div(className="col-md-5 col-xs-5"):
                ExecutionTime.dict_table(
                    name="Test info",
                    dictionary=profile.test_info
                )

                if middle_additions:
                    middle_additions(profile)

            with tags.div(className="col-md-4 col-xs-4"):
                if right_additions:
                    right_additions(profile)

    @abstractmethod
    def table(self, profile: Profile, category: str):
        pass

    def tables(
            self,
            profile: Profile,
            categories: List[str]):
        with tags.div(className="row"):
            for category in categories:
                self.table(profile, category)

    def run_single(
            self,
            profile: Profile,
            categories: List[str],
            title: Callable,
            intro: Callable):
        doc_title = title(profile)

        def children():
            intro(profile)
            self.tables(profile, categories)

        return layout(
            doc_title=doc_title,
            children=children,
            back_to_top=True,
            path_prefix="../"
        )


class ExecutionTimeJC(Page, ExecutionTime):
    TABLE_HEADER = [
        "Name of function",
        "Operation average (ms/op)",
        "Operation minimum (ms/op)",
        "Operation maximum (ms/op)",
        "Data length (bytes)",
        "Prepare average (ms/op)",
        "Prepare minimum (ms/op)",
        "Prepare maximum (ms/op)",
        "Iterations & Invocations",
    ]
    SUBFOLDER_NAME = "run_time"
    FILENAME = "execution-time.html"
    PATH = f"{SUBFOLDER_NAME}/{FILENAME}"

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceFixedJC] = profiles

    @staticmethod
    def get_table_data(profile: ProfilePerformanceFixedJC, category: str):
        category_results = [
            result
            for _, result in profile.results.items()
            if result.category.value == category
        ]
        return [
            [
                r.name,
                format(r.operation_avg(), ".2f"),
                format(r.operation_min(), ".2f"),
                format(r.operation_max(), ".2f"),
                r.data_length,
                r.baseline_avg(),
                r.baseline_min(),
                r.baseline_max(),
                f"{r.iterations}/{r.invocations}"
            ]
            if r.status == "OK"
            else [r.name, r.status]
            for r in category_results
        ]

    @overrides
    def table(self, profile: Profile, category: str):
        tags.h3(category, id=category)
        simple_table(
            data=ExecutionTimeJC.get_table_data(profile, category),
            table_header=ExecutionTimeJC.TABLE_HEADER
        )

    @overrides
    def run(self, output_path: str):
        def title(profile: ProfilePerformanceFixedJC):
            return f"JCAlgTest - {profile.device_name()} run time"

        def heading(profile: ProfilePerformanceFixedJC):
            tags.h1(f"Run time results - {profile.device_name()}")

        categories = list(map(lambda x: x.value, list(MeasurementCategory)))

        def middle_additions(profile: ProfilePerformanceFixedJC):
            with tags.div(className="row alert alert-primary"):
                tags.a(
                    "More information parsed from ATR",
                    href="https://smartcard-atr.apdu.fr"
                         f"/parse?ATR={profile.test_info['Card ATR']} "
                )

        def right_additions(profile: ProfilePerformanceFixedJC):
            ExecutionTime.dict_table("CPLC info", profile.cplc)

        output_path = f"{output_path}/{ExecutionTimeJC.SUBFOLDER_NAME}"
        data = run_helper(
            output_path,
            self.profiles,
            partial(
                self.run_single,
                title=title,
                categories=categories,
                intro=partial(
                    ExecutionTime.intro,
                    categories=categories,
                    heading=heading,
                    middle_additions=middle_additions,
                    right_additions=right_additions
                )
            )
        )
        data = list(map(
            lambda item: (item[0], f"./{item[0]}.html"),
            data
        ))
        with open(f"{output_path}/{ExecutionTimeJC.FILENAME}", "w") as f:
            f.write(
                cardlist(
                    data,
                    "JCAlgTest - Algorithm execution time",
                    ExecutionTimeJC.cardlist_text,
                    ExecutionTimeJC.cardlist_img,
                    None,
                )
            )

    @staticmethod
    def cardlist_text():
        tags.h1("Algorithm execution time")
        tags.p(
            "HTML page is generated from CSV file for each card. "
            "Test details (e.g., date, JCAlgTest version), "
            "JavaCard version, available memory and CPLC information "
            "are located at the beginning."
        )
        p = tags.p()
        p.add("We selected 25 frequently used functions and marked them as")
        p.add(tags.a("TOP FUNCTIONS", href="../top-function.html"))
        p.add(".")
        tags.p(
            "Each row of the table contains the name of measured function, "
            "time of execution (average, minimum, maximum), data length "
            "and minor information such as preparation time (average, "
            "minimum, maximum) and a number of test runs. If there is an "
            "unsupported algorithm or specific value returned by card, "
            "information is written in the row."
        )
        tags.p(
            "Rest of page consists of 20 tables presenting each "
            "group of tested methods."
        )

    @staticmethod
    def cardlist_img():
        tags.img(
            src="../pics/run_time_example.png",
            alt="Run time table example",
            className="img-fluid",
            align="right",
        )


class ExecutionTimeTPM(Page, ExecutionTime):
    FILENAME = "execution-time.html"
    SUBFOLDER_NAME = "run-time-tpm"
    H_DEPENDANT = {
        'TPM2_Create': [
            'Key parameters'
        ],
        'TPM2_EncryptDecrypt': [
            'Algorithm',
            'Key length',
            'Mode',
            'Encrypt/decrypt?'
        ],
        'TPM2_GetRandom': [
            'Data length (bytes)'
        ],
        'TPM2_Hash': [
            'Hash algorithm',
            'Data length (bytes)'
        ],
        'TPM2_RSA_Decrypt': [
            'Key parameters',
            'Scheme'
        ],
        'TPM2_RSA_Encrypt': [
            'Key parameters',
            'Scheme'
        ],
        'TPM2_Sign': [
            'Key parameters',
            'Scheme'
        ],
        'TPM2_VerifySignature': [
            'Key parameters',
            'Scheme'
        ]
    }
    H_DEFAULT = [
        'Operation average (ms/op)',
        'Operation minimum (ms/op)',
        'Operation maximum (ms/op)',
        'Iterations',
        'Successful',
        'Failed',
        'Error code'
    ]

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceTPM] = profiles

    @staticmethod
    def get_table_data(profile: ProfilePerformanceTPM, category: str):
        category_results = [
            result
            for _, result in profile.results.items()
            if result.category == category
        ]
        data = []

        for result in category_results:
            category_dependant: Dict[str, list[any]] = {
                'TPM2_Create': [
                    result.key_params
                ],
                'TPM2_EncryptDecrypt': [
                    result.algorithm,
                    result.key_length,
                    result.mode,
                    result.encrypt_decrypt,
                    result.data_length
                ],
                'TPM2_GetRandom': [
                    result.data_length
                ],
                'TPM2_Hash': [
                    result.algorithm,
                    result.data_length
                ],
                'TPM2_RSA_Decrypt': [
                    result.key_params,
                    result.scheme
                ],
                'TPM2_RSA_Encrypt': [
                    result.key_params,
                    result.scheme
                ],
                'TPM2_Sign': [
                    result.key_params,
                    result.scheme
                ],
                'TPM2_VerifySignature': [
                    result.key_params,
                    result.scheme
                ]
            }
            default = [
                result.operation_avg,
                result.operation_min,
                result.operation_max,
                result.iterations,
                result.successful,
                result.failed,
                result.error
            ]
            data.append(category_dependant[category] + default)

        return data

    @overrides
    def table(self, profile: Profile, category: str):
        data = ExecutionTimeTPM.get_table_data(profile, category)
        if data:
            tags.h3(category, id=category)
            simple_table(
                data=data,
                table_header=
                ExecutionTimeTPM.H_DEPENDANT[category]
                + ExecutionTimeTPM.H_DEFAULT
            )

    @overrides
    def run(self, output_path: str):
        def title(profile: ProfilePerformanceTPM):
            return f"tpm-algtest - {profile.device_name()} run time"

        def heading(profile: ProfilePerformanceTPM):
            tags.h1(f"Run time results - {profile.device_name()}")

        categories = ExecutionTimeTPM.H_DEPENDANT.keys()

        output_path = f"{output_path}/{ExecutionTimeTPM.SUBFOLDER_NAME}"
        data = run_helper(
            output_path,
            self.profiles,
            partial(
                self.run_single,
                title=title,
                categories=categories,
                intro=partial(
                    ExecutionTime.intro,
                    categories=categories,
                    heading=heading,
                )
            )
        )
        data = list(map(
            lambda item: (item[0], f"./{item[0]}.html"),
            data
        ))
        with open(f"{output_path}/{ExecutionTimeJC.FILENAME}", "w") as f:
            f.write(
                cardlist(
                    data,
                    "tpm-algtest - Algorithm execution time",
                    ExecutionTimeTPM.cardlist_text,
                    None,
                    None,
                )
            )

    @staticmethod
    def cardlist_text():
        tags.h1("Algorithm execution time")
        tags.p("HTML page is generated from CSV files for each TPM.")
