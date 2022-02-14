from math import sqrt
from typing import List, Dict, Tuple

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.config import SimilarityFunctions
from algtestprocess.modules.jcalgtest import ProfilePerformanceFixedJC
from algtestprocess.modules.pages.page import Page

ProfilePairSimilarity = Dict[
    Tuple[ProfilePerformanceFixedJC, ProfilePerformanceFixedJC], float
]


class Similarity(Page):
    FILENAME = "similarity-table.html"
    PATH = FILENAME

    def __init__(self, profiles):
        self.profiles: List[ProfilePerformanceFixedJC] = profiles

    @staticmethod
    def intro():
        tags.h1("Similarity of smart cards based on their performance")
        tags.h4(
            "The actual performance of tested card when executing "
            "required algorithm can be used as useful side-channel "
            "for fingerprinting purposes."
        )
        tags.br()
        tags.p(
            "Each cell in the table represents the (di-) similarity of "
            "two cards. A value close to 100% means that these two cards "
            "are very similar, whereas going to 0% mean significant "
            "dissimilarity. When a cursor is placed above value, tooltip "
            "showing difference in supported algorithms of exact two cards "
            "appears."
        )
        tags.p(
            "From the practical experience, we can say that pair of cards "
            "with similarity value over 95% means either the identical card "
            "type or both being members of the same product family with same "
            "underlying hardware and very similar implementation of JavaCard "
            "Virtual Machine. The similarity in the range of 85% - 95% usually "
            "signals the same family of cards yet with detectable differences "
            "(possibly different co-processor for some of the supported "
            "algorithms). The global average is about 70%, with similarity "
            "below 50% encountered for cards from completely different "
            "manufacturers."
        )
        tags.br()
        tags.h4("Why does it work?")
        tags.p(
            "In contrast to ordinary computers, smart cards are on one side "
            "more deterministic (usually, no processes running in parallel) "
            'yet more specialized on the hardware level. There is not "just" '
            "single general purpose CPU running compiled cryptographic "
            "algorithm, but a set of specialized circuits dedicated to the "
            "acceleration of particular cryptographic algorithm (DES, AES, "
            "RSA, ECC co-processor), all optimized for the maximum speed and "
            "minimum die space. Performance measurements of cryptographic "
            "algorithms can be therefore used as a card's fingerprint which "
            "cannot be easily manipulated on the higher software level. For "
            "example, one cannot re-implement faster RSA on the card's main "
            "CPU to mimic the speed of another card. The fastest achievable "
            "modular multiplication, on that particular card, is given by the "
            "performance of card's co-processor circuit and cannot be improved "
            "by the main CPU."
        )

    def normalize(self, functions):
        normalized = {}
        for f in functions:
            max_avg = max(
                [
                    profile.results[f].operation_avg()
                    if f in profile.results and profile.results[f].operation
                    else 0
                    for profile in self.profiles
                ]
            )
            normalized[f] = {}
            for profile in self.profiles:
                if f in profile.results and profile.results[f].baseline:
                    normalized[f][profile] = (
                        profile.results[f].operation_avg() / max_avg
                    )
                else:
                    normalized[f][profile] = 0
        return normalized

    def compute(self, functions: List[str]) -> ProfilePairSimilarity:
        normalized = self.normalize(functions)
        similarity = {}
        for p1 in self.profiles:
            for p2 in self.profiles:
                if p1 == p2:
                    continue
                total = 0
                num = 0
                for f in functions:
                    if normalized[f][p1] != 0 and normalized[f][p2] != 0:
                        total += (normalized[f][p1] - normalized[f][p2]) ** 2
                        num += 1
                total = abs(sqrt(total / num) - 1) if total != 0 else 0
                total = total ** 2
                similarity[(p1, p2)] = total
        return similarity

    def sorted_profiles(self):
        groups = SimilarityFunctions.GROUPS
        similarities = [self.compute(group) for group in groups]
        pairs = []
        for p1 in self.profiles:
            total = 0
            for p2 in self.profiles:
                if p1 == p2:
                    continue
                for s in similarities:
                    total += s[(p1, p2)]
            pairs.append((p1, total))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return list(map(lambda x: x[0], pairs))

    def compare_table_header(self):
        with tags.tr():
            tags.th("RSA")
            tags.th("RSA CRT")
            tags.th("ECC")
            for profile in self.profiles:
                tags.th(
                    profile.test_info["Card name"],
                    colspan=3,
                    rowspan=2,
                )
        with tags.tr():
            tags.th("Enc")
            tags.th("Hash")
            tags.th("SW")

    @staticmethod
    def compare_table_row(
        p1: ProfilePerformanceFixedJC,
        p2: ProfilePerformanceFixedJC,
        similarities: List[ProfilePairSimilarity],
    ):
        for similarity in similarities:
            style = "width: 3em; height: 3em;"
            s = similarity.get((p1, p2))
            color = (
                f"140, 200, 120, {format(s, '.2f')}"
                if s > 0.5
                else f"200, 120, 140, {format(1 - s, '.2f')}"
            )
            rounded = round(100 * s)
            style += (
                f"background: rgba({color});"
                if rounded != 0
                else "background: #f5f5f5"
            )
            tags.td(
                rounded if rounded != 0 else "",
                style=style,
            )

    def compare_table(self):
        self.profiles = self.sorted_profiles()
        groups = SimilarityFunctions.GROUPS
        similarities = [self.compute(group) for group in groups]

        with tags.table(className="compare", cellspacing=0):
            with tags.tbody():
                self.compare_table_header()
                for p1 in self.profiles:
                    for i, sim in enumerate(
                        [similarities[:3], similarities[3:]]
                    ):
                        with tags.tr():
                            if i == 0:
                                tags.th(
                                    p1.test_info["Card name"],
                                    colspan=3,
                                    rowspan=2,
                                )
                            for p2 in self.profiles:
                                style = "width: 3em; height: 3em;"
                                if p1 == p2:
                                    cls = "inactive"
                                    tags.td(className=cls, style=style)
                                    tags.td(className=cls, style=style)
                                    tags.td(className=cls, style=style)
                                    continue
                                Similarity.compare_table_row(p1, p2, sim)

    def run_single(self):
        doc_title = "JCAlgTest - Comparative table"

        def children_outside():
            with tags.div(className="container-fluid pt-5"):
                with tags.div(className="flex row pt-5"):
                    Similarity.intro()
                with tags.b():
                    self.compare_table()

        return layout(
            doc_title=doc_title,
            children_outside=children_outside
        )

    @overrides
    def run(self, output_path: str):
        with open(f"{output_path}/{Similarity.FILENAME}", "w") as f:
            f.write(self.run_single())
