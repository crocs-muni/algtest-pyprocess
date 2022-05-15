from functools import partial
from typing import Dict, List, Tuple, Union, Callable, Optional

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.cardlist import cardlist
from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.utils import AssetsPaths
from algtestprocess.modules.config import TopFunctionsJC
from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC, \
    PerformanceResultJC
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.utils import run_helper_multi
from algtestprocess.modules.tpmalgtest import ProfilePerformanceTPM, \
    PerformanceResultTPM

Profile = Union[ProfilePerformanceFixedJC, ProfilePerformanceTPM]


class Radar:

    def normalize(
            self,
            top_functions: List[Tuple[str, str]],
            profiles: List[Profile],
            operation_avg: Callable
    ) -> Dict[str, Dict[Profile, float]]:
        """
        Normalize the operation times for comparison across all profiles
        :param top_functions: functions which are normalized
        :param profiles: profiles
        :param operation_avg: function which gets the avg_op time from result
        :return: dict[function][profile] returns normalized values
        """
        normalized = {}
        for _, f in top_functions:
            max_avg = max(
                [
                    operation_avg(profile.results.get(f))
                    for profile in profiles
                ]
            )
            normalized[f] = {}
            for profile in profiles:
                if f in profile.results and max_avg > 0:
                    normalized[f][profile] = \
                        operation_avg(profile.results[f]) / (1.11 * max_avg)
                else:
                    normalized[f][profile] = 0

        return normalized

    def get_graph(
            self,
            profiles: List[Profile],
            top_functions: List[Tuple[str, str]],
            normalized: Dict[str, Dict[Profile, float]],
            operation_avg: Callable,
            hide_axes: bool = False
    ):
        """
        Creates graph script data for n > 1 profiles in the same chart
        :param profiles: chosen to be compared
        :param top_functions: which will create axes of the radar chart
        :param normalized: values
        :param operation_avg: lambda for getting op_avg from result
        :param hide_axes: optionally can hide axes to prevent clutter
        :return: script html object
        """
        script = tags.script()
        script.add(
            "var w = document.getElementById('chart').offsetWidth;"
            "var h = window.innerHeight -70;"
            "var colorscale = d3.scale.category10();"
        )
        script.add("var data = [")
        for profile in profiles:
            script.add("[")
            for info, name in top_functions:
                script.add(
                    "{"
                    f"axis:'{info if not hide_axes else ''}',"
                    "value:"
                    + format(
                        1 - normalized[name][profile]
                        if normalized.get(name)
                           and normalized.get(name).get(profile)
                           and normalized[name][profile] != 0
                        else 0,
                        ".3f",
                    )
                    + ","
                      "title:'"
                    + (
                        (f"{info} ") +
                        f"{format(operation_avg(profile.results[name]),'.2f')} ms"
                        if name in profile.results
                        else "NS"
                    )
                    + "'},"
                )
            script.add("],")
        script.add("];")
        script.add(
            "var config = { "
            "w: w-175,"
            "h: h-175,"
            "maxValue: 1.0,"
            "levels: 10,"
            "};"
        )
        script.add("RadarChart.draw('#chart', data, config);")
        return script

    def run_single(
            self,
            profiles: List[Profile],
            intro: Callable,
            get_graph: Callable,
            title: Callable,
            notebook: bool = False,
            device: str = 'javacard'
    ):
        """
        Creates a radar graph page for given list of profiles which are compared
        :param profiles: chosen to be compared
        :param intro: function which may create introductory part
        :param get_graph: partial function which is when called creates a script
        :param title: function which creates title
        :param notebook: optional script inline, usable in jupyter notebooks
        :param device: tpm or device, header depends on it
        :return: html visualization
        """
        doc_title = title(profiles)

        additions = [
            AssetsPaths.D3_JS,
            AssetsPaths.RADAR_JS
        ]

        def children():
            intro(profiles)
            tags.div(id="chart", className="col")

        get_graph.keywords['profiles'] = profiles
        other_scripts = [
            get_graph
        ]

        return layout(
            doc_title=doc_title,
            asset_additions=additions,
            children=children,
            other_scripts=other_scripts,
            back_to_top=True,
            path_prefix="../",
            notebook=notebook,
            device=device
        )


class RadarJC(Radar, Page):
    TOP_FUNCTIONS = TopFunctionsJC.SYM + TopFunctionsJC.ASYM
    SUBFOLDER_NAME = "radar_graphs"
    FILENAME = "radar-graphs.html"
    PATH = f"{SUBFOLDER_NAME}/{FILENAME}"

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceFixedJC] = profiles
        self.normalized: Dict[
            str, Dict[ProfilePerformanceFixedJC, float]
        ] = self.normalize(
            top_functions=RadarJC.TOP_FUNCTIONS,
            profiles=profiles,
            operation_avg=lambda result:
            result.operation_avg() if result and result.operation else 0
        )

    @staticmethod
    def intro(profile: ProfilePerformanceFixedJC):
        tags.h1(profile.test_info["Card name"], className="pt-5")
        p = tags.p()
        p.add(
            "Radar graph provides visual overview of Java Card performance."
            " It is composed of 25 frequently used functions "
        )
        p.add("(")
        p.add(tags.a("TOP FUNCTIONS", href="../top-functions.html"))
        p.add(")")
        tags.p(
            "The closest value to 100% represents the fastest result "
            "in particular method from all tested cards. Values closer to"
            " 10% supply slower results. 0% value means unsupported or not"
            " tested algorithms."
        )

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        def intro(profiles: List[ProfilePerformanceFixedJC]):
            return self.intro(profiles[0])

        def title(profiles: List[ProfilePerformanceFixedJC]):
            return f"JCAlgTest - {profiles[0].device_name()} radar graph"

        def operation_avg(result: PerformanceResultJC):
            return result.operation_avg() if result.operation else 0

        output_path = f"{output_path}/{RadarJC.SUBFOLDER_NAME}"
        data = run_helper_multi(
            output_path,
            items=[[profile] for profile in self.profiles],
            run_single=partial(
                self.run_single,
                title=title,
                intro=intro,
                get_graph=partial(
                    self.get_graph,
                    top_functions=RadarJC.TOP_FUNCTIONS,
                    normalized=self.normalized,
                    operation_avg=operation_avg
                ),
                notebook=notebook
            ),
        )
        data = list(map(
            lambda name: (name, f"./{name}.html"),
            data.values()
        ))
        with open(f"{output_path}/{RadarJC.FILENAME}", "w") as f:
            f.write(
                cardlist(
                    data,
                    "JCAlgTest - Performance radar graphs",
                    RadarJC.cardlist_text,
                    RadarJC.cardlist_img,
                    RadarJC.cardlist_alert,
                )
            )

    @staticmethod
    def cardlist_text():
        tags.h1("Performance radar graphs")
        tags.h4(
            "Radar graph provides visual overview of Java Card performance."
        )
        p = tags.p()
        p.add("It is composed of 25 frequently used functions ")
        p.add("(")
        p.add(tags.a("TOP FUNCTIONS", href="../top-function.html"))
        p.add(")")
        tags.p(
            "The closest value to 100% represents the fastest result "
            "in particular method from all tested cards. Values closer "
            "to 10% supply slower results. 0% value means unsupported or "
            "not tested algorithms.The closest value to 100% represents "
            "the fastest result in particular method from all tested cards."
            " Values closer to 10% supply slower results. 0% value means "
            "unsupported or not tested algorithms."
        )
        tags.p(
            "After hovering pointer above some point, the actual "
            "execution time of algorithm will be displayed."
        )

    @staticmethod
    def cardlist_img():
        tags.img(
            src="../pics/radar_chart_example.png",
            alt="Radar chart example",
            className="img-fluid",
            align="right",
        )

    @staticmethod
    def cardlist_alert():
        with tags.div(className="alert alert-info"):
            p = tags.p()
            p.add("We generate radar graphs for ")
            p.add(tags.a("TOP FUNCTIONS", href="../top-function.html"))
            p.add(
                "only to preserve clarity of results. "
                "You can find detailed test results in "
            )
            p.add(
                tags.a(
                    "PERFORMANCE TESTING - EXECUTION TIME",
                    href="../run_time/execution-time.html",
                )
            )
            p.add(" section.")


class RadarTPM(Radar, Page):
    FILENAME = "radar-graphs.html"
    SUBFOLDER_NAME = "radar-graphs-tpm"
    # There are no TOP FUNCTIONS for TPMs, so all found fuctions
    # create the axis
    TOP_FUNCTIONS = lambda profiles: sorted(list(set([
        (key.replace('TPM2_', '').replace('ALG_', '')
         .replace('ECC_', '').replace('EncryptDecrypt ',''),
         key)
        for profile in profiles
        for key in profile.results.keys()]
    )))

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceTPM] = profiles
        self.normalized: Dict[str, Dict[ProfilePerformanceTPM, float]] \
            = self.normalize(
            top_functions=RadarTPM.TOP_FUNCTIONS(profiles),
            profiles=profiles,
            operation_avg=lambda result: result.operation_avg
            if result and result.operation_avg else 0
        )

    def intro(self, profile: ProfilePerformanceTPM):
        tags.h1(profile.test_info['TPM name'], className="pt-5")
        tags.h3("Radar graph provides visual overview of TPM performance")

    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        def intro(profiles: List[ProfilePerformanceTPM]):
            return self.intro(profiles[0])

        def title(profiles: List[ProfilePerformanceTPM]):
            return f"tpm-algtest - {profiles[0].device_name()}"

        def operation_avg(result: PerformanceResultTPM):
            return result.operation_avg if result.operation_avg else 0

        output_path = f"{output_path}/{RadarTPM.SUBFOLDER_NAME}"
        data = run_helper_multi(
            output_path,
            items=[[profile] for profile in self.profiles],
            run_single=partial(
                self.run_single,
                title=title,
                intro=intro,
                get_graph=partial(
                    self.get_graph,
                    top_functions=RadarTPM.TOP_FUNCTIONS(self.profiles),
                    normalized=self.normalized,
                    operation_avg=operation_avg,
                    hide_axes=False
                ),
                notebook=notebook,
                device='tpm'
            )
        )
        data = list(map(
            lambda name: (name, f"./{name}.html"),
            data.values()
        ))

        html = cardlist(
            data,
            "tpm-algtest - Performance radar graphs",
            RadarTPM.cardlist_text,
            device='tpm'
        )

        if output_path:
            with open(f"{output_path}/{RadarTPM.FILENAME}", "w") as f:
                f.write(html)

        data = list(map(
            lambda item: (item[0], f"{output_path}/{item[1]}"), data))
        return html, data


    @staticmethod
    def cardlist_text():
        tags.h1("Performance radar graphs")
        tags.h4(
            "Radar graph provides visual overview of TPM performance."
        )
