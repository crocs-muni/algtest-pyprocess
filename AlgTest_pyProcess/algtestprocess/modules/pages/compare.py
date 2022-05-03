import os
from functools import partial

from typing import Tuple, List, Callable, Dict, Union, Optional

from dominate import tags
from overrides import overrides

from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC, \
    PerformanceResultJC
from algtestprocess.modules.pages.radar import Radar, RadarJC
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.utils import run_helper_multi
from algtestprocess.modules.tpmalgtest import ProfilePerformanceTPM


def colored_span(name: str, color: str):
    return tags.span(name, style=f"color: {color};")


Profile = Union[ProfilePerformanceFixedJC, ProfilePerformanceTPM]


class Compare(RadarJC, Page):
    SUBFOLDER_NAME = "compare"

    def __init__(self, profiles: List[ProfilePerformanceFixedJC]):
        super(Compare, self).__init__(profiles)

    def intro(self, profiles: List[Profile]):
        p1, p2 = profiles[0], profiles[1]
        name1 = p1.device_name()
        name2 = p2.device_name()
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

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        def title(profiles: List[ProfilePerformanceFixedJC]):
            return f"JCAlgtest - {profiles[0].device_name()} " \
                   f"vs {profiles[1].device_name()} radar graph"

        def operation_avg(result: PerformanceResultJC):
            return result.operation_avg() if result.operation else 0

        output_path = f"{output_path}/{Compare.SUBFOLDER_NAME}"
        data = run_helper_multi(
            output_path=output_path,
            items=[[p1, p2] for p1 in self.profiles
                   for p2 in self.profiles if p1 != p2],
            run_single=partial(
                self.run_single,
                title=title,
                intro=self.intro,
                get_graph=partial(
                    self.get_graph,
                    top_functions=RadarJC.TOP_FUNCTIONS,
                    normalized=self.normalized,
                    operation_avg=operation_avg
                )
            )
        )
        return data