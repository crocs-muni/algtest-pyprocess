from functools import partial
from typing import List, Callable, Dict

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.config import SupportGroups
from algtestprocess.modules.jcalgtest import ProfileSupportJC
from algtestprocess.modules.pages.page import Page


def colored_cell(tag: Callable, content: str):
    cls = "light_info"
    if content == "yes" or content == "no":
        cls = f"light_{content}"
    if content == "-":
        cls = "light_maybe"
    tag(content, className=cls)


def checkall_script(key: str, cards: List[str]):
    """Checkbox functionality script"""
    script = tags.script()
    script.add(
        f"function checkAll{key}(divid)"
        "{"
        "uncheckAll(divid);"
        f"let array = {cards};"
        "for (let cardName of array) {"
        "let obj = document.getElementById(cardName);"
        "$(obj).prop('checked', true);"
        "processToggle($(obj), true);"
        "}"
        "}"
    )


class Support(Page):
    FILENAME = "table.html"
    PATH = FILENAME
    CATEGORIES = [
        "javacardx.crypto.Cipher",
        "javacard.crypto.Signature",
        "javacard.security.MessageDigest",
        "javacard.security.RandomData",
        "javacard.security.KeyBuilder",
        "javacard.security.KeyPair ALG_RSA on-card generation",
        "javacard.security.KeyPair ALG_RSA_CRT on-card generation",
        "javacard.security.KeyPair ALG_DSA on-card generation",
        "javacard.security.KeyPair ALG_EC_F2M on-card generation",
        "javacard.security.KeyPair ALG_EC_FP on-card generation",
        "javacard.security.KeyAgreement",
        "javacard.security.Checksum",
        "Variable RSA 1024"
    ]

    def __init__(self, profiles):
        self.profiles: List[ProfileSupportJC] = \
            sorted(profiles, key=lambda x: x.test_info["Card name"].upper())

    def intro(self):
        with tags.div(className="col-xl-9"):
            tags.h1("List of supported JavaCard algorithms")
            tags.h4(
                "The table provides a list of algorithms defined in JavaCard API "
                "and supported by the particular smart card. The supported lengths "
                "of cryptographic keys, information about available RAM and EEPROM "
                "memory and garbage collection capabilities are also included."
            )
            tags.p(
                "The set of cryptographic algorithms supported by the "
                "particular Java smart card is sometimes hard to obtain "
                "from vendor's specifications. Moreover, supported "
                "algorithms may change in more recent revisions of the "
                "firmware of given type of smart card. Typically, basic "
                "primitives like block cipher or asymmetric cryptography "
                "algorithm remain same as they are often implemented in "
                "hardware, but cryptographic constructions like particular "
                "MAC algorithm or supported key sizes may be added later."
            )
            p = tags.p()
            p.add(
                "JCAlgTest tool allows you to enumerate the supported cryptographic "
                "algorithms specified in JavaCard 3.0.5 and earlier. This page "
                "summarizes results obtained for cards available in our CRoCS "
                "laboratory and also results contributed by the community "
            )
            p.add(tags.b("(Many thanks folks!)"))
            p.add(tags.br())
            # Add credits for card result donors
            for name, value in self.get_donors().items():
                name = name.lstrip("(provided by ")
                name = name.rstrip(")")
                p.add(f"{name} ({value}x), ")
            tags.p(
                "The basic idea is simple - if the particular algorithm/key size "
                "is supported, then algorithm instance creation should succeed. "
                "Otherwise, CryptoException.NO_SUCH_ALGORITHM is thrown. Such a "
                "behavior can be employed for a quick test of supported algorithms."
                " AlgTest applet tries to create an instance of an algorithm for "
                "all possible constants defined in JavaCard specification and "
                "eventually catch the exception. JCAlgTest tool also tests "
                "additional tweaks like the possibility to use raw RSA for fast "
                "modular multiplication (which is usable to implement classical "
                "Diffie-Hellman key exchange) or manufacturer pre-set default ECC "
                "curve for ECC key pair."
            )
        with tags.div(className="col-xl-3 justify-content-center"):
            tags.img(
                src="pics/numCardsInDB.png",
                alt="Number of cards in the DB",
                className="img-fluid"
            )

    def get_donors(self):
        donation_credits = {}
        for profile in self.profiles:
            donator = profile.test_info["Provider"]
            if not donator:
                continue
            if donation_credits.get(donator) is None:
                donation_credits[donator] = 0
            donation_credits[donator] += 1
        return donation_credits

    def abbreviations(self):
        tags.h3("Tested cards abbreviations")
        for i in range(len(self.profiles)):
            tags.b(f"c{i}")
            tags.a(
                self.profiles[i].test_info["Card name"],
                href=self.profiles[i].test_info["Github link"]
            )
            tags.span(", ATR=" + self.profiles[i].test_info["Card ATR"])
            tags.span(self.profiles[i].test_info["Provider"])
            tags.br()

    def notes(self):
        tags.br()
        tags.p(
            "Note: Some cards in the table come without full identification "
            "and ATR ('undisclosed') as submitters prefered not to disclose "
            "it at the momment. I'm publishing it anyway as the information "
            "that some card supporting particular algorithm exists is still "
            "interesting. Full identification might be added in future."
        )
        p = tags.p()
        p.add(
            "Note: If you have card of unknown type, try to obtain ATR and "
            "take a look at smartcard list available here:"
        )
        p.add(tags.a("https://smartcard-atr.apdu.fr/",
                     href="https://smartcard-atr.apdu.fr"))

    def filter_by_support(self):
        cards = {}
        for key, algs in SupportGroups.GROUPS:
            cards[key] = [
                f"card{i}" for i in range(len(self.profiles))
                if any([
                    self.profiles[i].results.get(alg) is not None and
                    self.profiles[i].results.get(alg).support
                    for alg in algs
                ])
            ]
        return cards

    def checkbox_buttons(self):
        filtered: Dict[str, List[str]] = self.filter_by_support()
        tags.input_(type="button", className="btn btn-outline-dark",
                    id="checkAll",
                    onclick="checkAll('grpChkBox')", value="Select all")
        tags.input_(type="button", className="btn btn-outline-dark",
                    id="uncheckAll",
                    onclick="uncheckAll('grpChkBox')", value="Deselect all")
        for key, cards in filtered.items():
            replaced = key.replace(" ", "_")
            checkall_script(replaced, cards)
            tags.input_(
                type="button", className="btn btn-outline-dark",
                onclick=f"checkAll{replaced}('grpChkBox')",
                id=f"checkAll{replaced}",
                value=f"Select all with {key}"
            )

    def checkbox_items(self):
        """Put checkboxes into three columns"""
        cols = 3
        curr = 0
        split = len(self.profiles) // cols
        curr_div = None
        for i in range(len(self.profiles)):
            if not curr_div or (curr * split < i and curr < cols):
                curr += 1
                curr_div = tags.div(className="col-lg-4 col-sm-4")
            p = tags.p(style="margin:0;")
            p.add(tags.input_(type="checkbox", name=f"{i}", id=f"card{i}"))
            p.add(tags.b(f"c{i}"))
            p.add(f" - {self.profiles[i].test_info['Card name']}")
            curr_div.add(p)

    def checkboxes(self):
        with tags.div(className="row", id="grpChkBox"):
            with tags.div(className="btn-group", role="group"):
                self.checkbox_buttons()
            self.checkbox_items()

    def category(self, name: str, rows: Callable):
        """Function to create category section in table"""
        with tags.tr():
            tags.td(name, className="dark")
            # TODO Introduced in JC ver. xxx column
            for i in range(len(self.profiles)):
                tags.th(
                    f"c{i}",
                    className=f"dark_index {i}",
                    title=self.profiles[i].test_info["Card name"]
                )
        rows()

    def basic_info_rows(self):
        for item in ["AlgTest applet version", "JavaCard support version"]:
            with tags.tr():
                tags.td(
                    item,
                    className="light"
                )
                for profile in self.profiles:
                    card_name = profile.test_info["Card name"]
                    version = profile.test_info.get(item)
                    content = version.strip(";") if version else "-"
                    colored_cell(
                        partial(
                            tags.td,
                            title=f"{card_name} : {item} : {content}"
                        ),
                        content
                    )

    def table_header(self):
        with tags.thead():
            self.category("Basic info", self.basic_info_rows)

    def jc_system_rows(self):
        all_keys = set([
            key for profile in self.profiles
            for key in profile.jcsystem.keys()
        ])
        for key in sorted(all_keys):
            with tags.tr():
                tags.td(key, className="light")
                for profile in self.profiles:
                    card_name = profile.test_info["Card name"]
                    value = profile.jcsystem.get(key)
                    content = value.split(";")[0] if value else "-"
                    colored_cell(
                        partial(
                            tags.td,
                            title=f"{card_name} : {key} : {content}"
                        ),
                        content
                    )

    def jc_system(self):
        self.category("javacard.framework.JCSystem", self.jc_system_rows)

    def javacard_main_rows(self, cat: str):
        """Create rows for given category"""
        all_keys = set([
            key for profile in self.profiles
            for key, _ in list(filter(
                lambda x: x[1].category == cat, profile.results.items()
            ))
        ])
        for key in sorted(all_keys):
            with tags.tr():
                tags.td(key, className="light")
                for profile in self.profiles:
                    card_name = profile.test_info["Card name"]
                    result = profile.results.get(key)
                    if not result:
                        colored_cell(tags.td, "-")
                    else:
                        content = ("yes" if result.support else "no") \
                            if result.status == "OK" else "error"
                        title = content if content in ["yes", "no"] \
                            else result.status
                        colored_cell(
                            partial(
                                tags.td,
                                title=f"{card_name} : {key} : {title}"
                            ),
                            content
                        )

    def javacard_main(self):
        """Create section for each category"""
        for cat in Support.CATEGORIES:
            self.category(cat, partial(self.javacard_main_rows, cat))

    def table(self):
        with tags.table(
                id="tab",
                width="37rem",
                border="0",
                cellspacing="2",
                cellpadding="4",
                className="table"
        ):
            self.table_header()
            with tags.tbody():
                self.jc_system()
                self.javacard_main()

    def run_single(self):
        doc_title = "JCAlgTest - Comparative table"

        def head_additions():
            tags.link(href="./dist/supporttable_style.css", rel="stylesheet")
            tags.script(src="./assets/js/checkboxes.js")

        def children_outside():
            with tags.div(className="container-fluid pt-5"):
                with tags.div(className="flex row pt-5"):
                    self.intro()
                self.abbreviations()
                self.notes()
                self.checkboxes()
                with tags.b():
                    self.table()

        return layout(
            doc_title=doc_title,
            head_additions=head_additions,
            children_outside=children_outside,
            back_to_top=True,
        )

    @overrides
    def run(self, output_path: str):
        with open(f"{output_path}/{Support.FILENAME}", "w") as f:
            f.write(self.run_single())
