from typing import Dict, List

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.cardlist import cardlist
from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.config import TopFunctions
from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.utils import run_helper


class Radar(Page):
    TOP_FUNCTIONS = TopFunctions.SYM + TopFunctions.ASYM
    SUBFOLDER_NAME = "radar_graphs"
    FILENAME = "radar-graphs.html"
    PATH = f"{SUBFOLDER_NAME}/{FILENAME}"

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceFixedJC] = profiles
        self.normalized: Dict[
            str, Dict[ProfilePerformanceFixedJC, float]
        ] = self.normalize()

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

    def normalize(self) -> Dict[str, Dict[ProfilePerformanceFixedJC, float]]:
        normalized = {}
        for _, f in Radar.TOP_FUNCTIONS:
            max_avg = max(
                [
                    profile.results[f].operation_avg()
                    if f in profile.results
                    and profile.results[f].operation
                    else 0
                    for profile in self.profiles
                ]
            )
            normalized[f] = {}
            for profile in self.profiles:
                if f in profile.results and profile.results[f].baseline:
                    normalized[f][profile] = \
                        profile.results[f].operation_avg() / (1.11 * max_avg)
                else:
                    normalized[f][profile] = 0

        return normalized

    def get_graph(self, profile: ProfilePerformanceFixedJC):
        script = tags.script()
        script.add(
            "var w = document.getElementById('chart').offsetWidth;"
            "var h = window.innerHeight -70;"
            "var colorscale = d3.scale.category10();"
        )
        script.add("var data = [[")
        for info, name in Radar.TOP_FUNCTIONS:
            script.add(
                "{"
                f"axis:'{info}',"
                "value:"
                + format(
                    1 - self.normalized[name][profile]
                    if self.normalized[name][profile] != 0
                    else 0,
                    ".3f",
                )
                + ","
                "title:'"
                + (
                    format(profile.results[name].operation_avg(), ".2f") + "ms"
                    if name in profile.results
                    and profile.results[name].operation
                    else "NS"
                )
                + "'},"
            )
        script.add("],];")
        script.add(
            "var config = { "
            "w: w-175,"
            "h: h-175,"
            "maxValue: 1.0,"
            "levels: 10,"
            "};"
        )
        script.add("RadarChart.draw('#chart', data, config);")

    def run_single(self, profile):
        doc_title = f"JCAlgTest - {profile.test_info['Card name']} radar graph"

        def head_additions():
            tags.script(src="../assets/js/d3.v3.min.js")
            tags.script(src="RadarChart.js")

        def children():
            Radar.intro(profile)
            tags.div(id="chart", className="col")

        def children_outside():
            self.get_graph(profile)

        return layout(
            doc_title=doc_title,
            head_additions=head_additions,
            children=children,
            children_outside=children_outside,
            back_to_top=True,
            path_prefix="../"
        )

    @overrides
    def run(self, output_path: str):
        output_path = f"{output_path}/{Radar.SUBFOLDER_NAME}"
        data = run_helper(output_path, self.profiles, self.run_single)
        with open(f"{output_path}/{Radar.FILENAME}", "w") as f:
            f.write(
                cardlist(
                    data,
                    "JCAlgTest - Performance radar graphs",
                    Radar.cardlist_text,
                    Radar.cardlist_img,
                    Radar.cardlist_alert,
                )
            )

    @staticmethod
    def cardlist_text():
        tags.h1("Performance radar graphs")
        tags.h4(
            "Radar graph provides visual overview " "of Java Card performance."
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
