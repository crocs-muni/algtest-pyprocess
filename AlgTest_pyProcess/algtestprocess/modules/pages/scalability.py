from typing import List, Tuple, Optional

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.cardlist import cardlist
from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.simpletable import simple_table
from algtestprocess.modules.jcalgtest import (
    ProfilePerformanceVariableJC,
    PerformanceResultJC,
)
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.pages.utils import run_helper, filtered_results


class Scalability(Page):
    FILENAME = "scalability.html"
    SUBFOLDER_NAME = "scalability"
    PATH = f"{SUBFOLDER_NAME}/{FILENAME}"

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceVariableJC] = profiles

    @staticmethod
    def intro(profile: ProfilePerformanceVariableJC):
        tags.h1(f"Run time results - {profile.test_info['Card name']}")
        p = tags.p(
            "The performance of the card and given algorithm changes "
            "with the length of processed data. Here we provide "
            "detailed performance for relevant methods expected to "
            "process input with variable lengths (e.g., "
            "Cipher.doFinal()). We measured the execution time for "
            "data lengths of 16, 32, 64, 128, 256 and 512 bytes and "
            "visualize in a graph. Multiple measurements of the same "
            "method and fixed data length are performed to capture its "
            "variability. Read more about how the measurement was done "
        )
        p.add(tags.a("here", href="scalability.html"))
        p.add(".")

    @staticmethod
    def quick_links(profile: ProfilePerformanceVariableJC):
        tags.h3("Quick links")
        with tags.ul():
            for name, _ in filtered_results(profile.results.items()):
                with tags.li():
                    tags.a(name, href="#" + name.replace(" ", ""))

    @staticmethod
    def test_details(profile: ProfilePerformanceVariableJC):
        tags.h3("Test details")
        data = [[key, val] for key, val in profile.test_info.items()]
        simple_table(data)

    @staticmethod
    def chart_scripts_begin():
        """
        Only script which cannot be inlined, allows for scalability
        chart creation.
        """
        tags.script(
            type="text/javascript",
            src="https://www.gstatic.com/charts/loader.js",
        )
        tags.script("google.charts.load('current', {packages: ['corechart']});")

    @staticmethod
    def chart_scripts_end():
        tags.script(
            type="text/javascript",
            src="https://www.gstatic.com/charts/loader.js",
        )

    @staticmethod
    def get_chart(result: Tuple[str, List[PerformanceResultJC]]):
        """
        Creates scalability chart
        :param result: (function name, measurement results with diff datalength)
        :return: script html object
        """
        name, methods = result
        s = tags.script(type="text/javascript")
        s.add(
            "google.setOnLoadCallback(drawFancyVisualization);"
            "function drawFancyVisualization() {"
            "var data = new google.visualization.DataTable();"
            "		data.addColumn('number', 'length of data (bytes)');"
            "       data.addColumn('number', 'Time (ms)');"
            "       data.addColumn({type:'number', role:'interval'});"
            "       data.addColumn({type:'number', role:'interval'});"
            "       data.addColumn({type:'string', role:'annotation'});"
            "       data.addColumn({type:'boolean',role:'certainty'});"
            "       data.addRows(["
        )
        for method in methods:
            if method.baseline:
                s.add(
                    f"["
                    f"{method.data_length},"
                    f"{format(method.operation_avg(), '.2f')},"
                    f"{format(method.operation_min(), '.2f')},"
                    f"{format(method.operation_max(), '.2f')},"
                    f"'{method.data_length}',"
                    f"false,"
                    f"],"
                )
        s.add("       ]);")
        max_len = max([method.data_length for method in methods]) + 18
        s.add(
            "var options = {"
            "backgroundColor: 'transparent',"
            "hAxis: {title: 'length of data (bytes)', "
            "viewWindow: {min: 0, max: " + str(max_len) + "} },"
            "vAxis: {title: 'duration of operation (ms)' },"
            "legend:'none',};"
        )
        s.add(
            f"var chart = new google.visualization.LineChart("
            f"document.getElementById('{name.replace(' ', '')}'));"
            "chart.draw(data, options);}"
        )

    @staticmethod
    def get_chart_placeholder(name: str):
        """
        Each chart needs div with id where chart can be rendered
        """
        div = tags.div(className="graph")
        div.add(tags.h4(name))
        div.add(
            tags.div(
                id=name.replace(" ", ""),
                style="min-height:479px; margin-top:-50px;",
            )
        )
        return div

    @staticmethod
    def get_charts(profile: ProfilePerformanceVariableJC):
        """Creates charts for functions in two columns"""
        cols = [tags.div(className="col-md-6"), tags.div(className="col-md-6")]
        count = 0
        for result in filtered_results(profile.results.items()):
            name, _ = result
            Scalability.get_chart(result)
            if count % 2 == 0 and count != 0:
                row = tags.div(className="row")
                row.add(cols[0])
                row.add(cols[1])
                cols = [tags.div(className="col-md-6"), tags.div(className="col-md-6")]
            cols[count % 2].add(Scalability.get_chart_placeholder(name))
            count += 1

    def run_single(self, profile: ProfilePerformanceVariableJC):
        doc_title = (
            f"JCAlgTest - {profile.test_info['Card name']} " f"scalability graph"
        )

        def children():
            with tags.div(className="row pt-5"):
                Scalability.intro(profile)
                with tags.div(className="col-md-7 col-xs-7"):
                    Scalability.quick_links(profile)
                with tags.div(className="col-md-5 col-xs-5"):
                    Scalability.test_details(profile)

        def children_outside():
            with tags.div(className="container-fluid px-5"):
                Scalability.chart_scripts_begin()
                with tags.div(className="row"):
                    Scalability.get_charts(profile)
                Scalability.chart_scripts_end()

        return layout(
            doc_title=doc_title,
            children=children,
            children_outside=children_outside,
            back_to_top=True,
            path_prefix="../",
        )

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        output_path = f"{output_path}/{Scalability.SUBFOLDER_NAME}"
        data = run_helper(
            output_path, self.profiles, self.run_single, desc="Scalability pages"
        )
        data = list(map(lambda pair: (pair[0], f"./{pair[0]}.html"), data))
        with open(f"{output_path}/{Scalability.FILENAME}", "w") as f:
            f.write(
                cardlist(
                    data,
                    "JCAlgTest - Scalability radar graphs",
                    Scalability.cardlist_text,
                    Scalability.cardlist_img,
                    Scalability.cardlist_alert,
                )
            )

    @staticmethod
    def cardlist_text():
        tags.h1("Length-dependent performance")
        tags.p(
            "The performance of the card and given algorithm changes "
            "with the length of processed data. Here we provide detailed "
            "performance for relevant methods expected to process input "
            "with variable lengths (e.g., Cipher.doFinal()). We measured "
            "the execution time for data lengths of 16, 32, 64, 128, 256 "
            "and 512 bytes and visualize in a graph. Multiple measurements "
            "of the same method and fixed data length are performed to "
            "capture its variability."
        )
        tags.p(
            "We also included measurements of several methods usually used "
            "together in single sequence (e.g., set key, init the engine "
            "and sign the data). Note that resulting time is not simply the "
            "sum of operations measured separately as JavaCard Virtual "
            "Machine itself influence the results same way as caching and "
            "other optimizations do for ordinary CPUs. Used key values are "
            "randomly generated to prevent JCVM optimizations by skipping "
            "already performed initialization."
        )
        tags.p(
            "Note that as many algorithms are block-based, you will "
            "experience almost the same execution time until the length "
            "of the process data exceeds the length of internal algorithm "
            "block (e.g, 64 bytes for SHA-2 hash) after which significantly "
            "more operations are executed to process another full block. "
            "Similar behavior but with a different underlying cause can be "
            "observed when the length in processed data exceeds the length "
            "of engine's internal memory buffers. Finally, it often makes "
            "sense to concatenate multiple independent blocks into a buffer "
            "and then call processing method only once as actual processing "
            "(e.g., encryption) is only part of the operation - context "
            "switch between card's main processor and crypto co-processor "
            "may be significant."
        )

    @staticmethod
    def cardlist_img():
        tags.img(
            src="../pics/scalability_example.png",
            alt="Scalability chart example",
            className="img-fluid",
            align="right",
        )

    @staticmethod
    def cardlist_alert():
        with tags.div(className="alert alert-info"):
            p = tags.p()
            p.add("It may take a few seconds to load all graphs on page.")
            p.add(tags.br())
            p.add(
                "Click on the target smart card to display its "
                "length-dependent performance. If you would like "
                "to see measurements of all operations please visit "
            )
            p.add(
                tags.a(
                    "Performance details page",
                    href="../run_time/execution-time.html",
                )
            )
            p.add(".")
