import itertools
import os
from functools import partial

from typing import Tuple, List, Callable, Dict

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC
from algtestprocess.modules.pages.radar import Radar

ProfilePair = Tuple[ProfilePerformanceFixedJC, ProfilePerformanceFixedJC]


def colored_span(name: str, color: str):
    return tags.span(name, style=f"color: {color};")


class Compare(Radar):
    SUBFOLDER_NAME = "compare"

    def __init__(self, profiles):
        super().__init__(profiles)

    def intro(self, profiles: ProfilePair):
        p1, p2 = profiles
        name1 = p1.test_info["Card name"]
        name2 = p2.test_info["Card name"]
        tags.h1(f"Comparison on {name1} and {name2}", className="pt-5")
        tags.p(
            "This is comparation radar graph of ",
            colored_span(name1, "blue"),
            " and ",
            colored_span(name2, "orange"),
            "."
        )
        tags.p(
            "The values closer to 100% represent the times close to the "
            "fastest result among all tested cards, whereas values close "
            "to 10% suggest slower performance in the corresponding algorithm. "
            "Value of 0%(NS) indicates a lack of support or occurrence of "
            "unexpected error during the tested algorithm."
        )

    def run_single(self, profiles: ProfilePair):
        p1, p2 = profiles
        doc_title = f"JCAlgtest - Comparison of {p1.test_info['Card name']} " \
                    f"and {p2.test_info['Card name']}"

        def head_additions():
            tags.script(src="../assets/js/d3.v3.min.js")
            tags.script(src="RadarChart.js")

        def children():
            self.intro(profiles)
            tags.div(id="chart", className="col")

        children_outside = partial(super().get_graph, [p1, p2])

        return layout(
            doc_title=doc_title,
            head_additions=head_additions,
            children=children,
            children_outside=children_outside,
            back_to_top=False,
            path_prefix="../"
        )

    def run_helper(
            self,
            output_path: str,
            pairs: List[ProfilePair],
            run_single: Callable
    ):
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        data: Dict[
            Tuple[
                ProfilePerformanceFixedJC, ProfilePerformanceFixedJC], str] = {}
        for p1, p2 in pairs:
            name1 = p1.test_info["Card name"]
            name2 = p2.test_info["Card name"]
            filename = f"{name1.replace(' ', '')}_vs_{name2.replace(' ', '')}"
            path = f"{output_path}/{filename}.html"
            with open(path, "w") as f:
                f.write(run_single([p1, p2]))
            data[(p1, p2)] = path
        return data

    @overrides
    def run(self, output_path: str):
        output_path = f"{output_path}/{Compare.SUBFOLDER_NAME}"
        data = self.run_helper(
            output_path,
            [(p1, p2) for p1 in self.profiles
             for p2 in self.profiles if p1 != p2],
            self.run_single
        )
        return data
