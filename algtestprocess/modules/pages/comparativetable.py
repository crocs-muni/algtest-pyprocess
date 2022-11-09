from typing import List, Optional

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.config import TopFunctionsJC
from algtestprocess.modules.components.simpletable import simple_table
from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC
from algtestprocess.modules.pages.page import Page


class ComparativeTable(Page):
    FILENAME = "comparative-table.html"
    PATH = FILENAME
    SWAES_LINK = "https://www.fi.muni.cz/~xsvenda/jcalgs.html#aes"

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceFixedJC] = profiles

    @staticmethod
    def intro():
        tags.h1("Comparative table", className="pt-5")
        tags.h4(
            "Simple Java card comparison is provided by "
            "the Comparative table. It allows sorting cards "
            "according to performance results for a particular algorithm."
        )
        tags.p(
            "Each row represents tested card, and column represents specific "
            "method. Cards can be sorted just by click on a name of the "
            "algorithm in the table header. Ascending and descending sorting "
            "are available."
        )
        tags.p(
            "Unsupported algorithms are supplied by '-' symbol and they "
            "are placed at the end of ascending sort. While hovering the "
            "cursor over any run time, minimum and maximum run times will "
            "be displayed."
        )

    @staticmethod
    def alert():
        tag = tags.div(className="alert alert-info", role="alert")
        tag.add("We generate comparative tables for ")
        tag.add((tags.a("TOP FUNCTIONS", href="./top-functions.html")))
        tag.add(
            " only to preserve clarity of results. First for symmetric "
            "and second for asymmetric cryptography algorithms. "
            "You can find detailed test results in "
        )
        tag.add(
            tags.a(
                "PERFORMANCE TESTING - EXECUTION TIME",
                href="./run_time/execution-time.html",
            )
        )

    def content(self):
        tf_data = [
            (TopFunctionsJC.SYM, "sortable_sym"),
            (TopFunctionsJC.ASYM, "sortable_asym"),
        ]
        for tf_type, tf_id in tf_data:
            with tags.ul():
                for name, signature in tf_type:
                    li = tags.li()
                    if name == "SWAES oneblock (16B)":
                        li.add(
                            tags.a(
                                tags.strong(name),
                                href=ComparativeTable.SWAES_LINK,
                            )
                        )
                    else:
                        li.add(tags.strong(name))
                    li.add(" = " + signature)

            t_header = ["CARD/FUNCTION (ms/op)"] + [info for info, _ in tf_type]
            data = [
                [profile.test_info["Card name"]]
                + [
                    format(profile.results[function].baseline_avg(), ".2f")
                    if function in profile.results
                    and profile.results[function].baseline
                    else "-"
                    for _, function in tf_type
                ]
                for profile in self.profiles
            ]
            simple_table(
                data,
                t_header,
                table_id=tf_id,
                table_cls="tablesorter",
                th_cls="header",
            )

    def run_single(self):
        doc_title = "JCAlgTest - Comparative table"

        def children():
            ComparativeTable.intro()
            ComparativeTable.alert()
            self.content()

        def children_outside():
            for table_id in ["#sortable_sym", "#sortable_asym"]:
                tags.script(
                    "$(document).ready(function() {"
                    f"$('{table_id}').DataTable("
                    "{'paging':false,'info':false"
                    "});"
                    "});"
                )
            tags.script(
                "$(document).ready(function() {"
                "$('#sortable_asym').DataTable();"
                "} );"
            )

        return layout(
            doc_title=doc_title,
            children=children,
            children_outside=children_outside
        )

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        html = self.run_single()

        if not notebook and output_path:
            with open(f"{output_path}/{ComparativeTable.FILENAME}", "w") as f:
                f.write(html)

        return html
