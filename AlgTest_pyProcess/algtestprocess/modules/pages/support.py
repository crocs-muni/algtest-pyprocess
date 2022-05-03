import re
from functools import partial
from typing import List, Callable, Dict, Set, Optional, Tuple, Union

from dominate import tags
from overrides import overrides

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.utils import AssetsPaths
from algtestprocess.modules.config import SupportGroups, TPM2Identifier
from algtestprocess.modules.jcalgtest import ProfileSupportJC, ProfileJC
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.tpmalgtest import ProfileSupportTPM, ProfileTPM


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


SupportGroup = Tuple[str, List[str]]

Profile = Union[ProfileSupportJC, ProfileSupportTPM]


class Support:

    def filter_by_support(
            self,
            device: str,
            support_groups: List[SupportGroup],
            profiles: List[Profile]):
        devices = {}
        for key, algs in support_groups:
            devices[key] = [
                f"{device}{i}" for i, profile in enumerate(profiles)
                if any([
                    profile.results.get(alg) is not None and
                    profile.results.get(alg).support
                    for alg in algs
                ])
            ]
        return devices

    def checkbox_buttons(
            self,
            device: str,
            support_groups: List[SupportGroup],
            profiles: List[Profile]):
        filtered: Dict[str, List[str]] = \
            self.filter_by_support(device, support_groups, profiles) \
                if support_groups else {}
        tags.input_(
            type="button",
            className="btn btn-outline-dark",
            id="checkAll",
            onclick="checkAll('grpChkBox')",
            value="Select all")
        tags.input_(
            type="button",
            className="btn btn-outline-dark",
            id="uncheckAll",
            onclick="uncheckAll('grpChkBox')",
            value="Deselect all")
        for key, devices in filtered.items():
            replaced = key.replace(" ", "_")
            checkall_script(replaced, devices)
            tags.input_(
                type="button",
                className="btn btn-outline-dark",
                onclick=f"checkAll{replaced}('grpChkBox')",
                id=f"checkAll{replaced}",
                value=f"Select all with {key}"
            )

    def checkbox_items(self, device: str, profiles: List[Profile]):
        """Put checkboxes into three columns"""
        cols = 3
        curr = 0
        split = len(profiles) // cols
        curr_div = None
        for i, profile in enumerate(profiles):
            if not curr_div or (curr * split < i and curr < cols):
                curr += 1
                curr_div = tags.div(className="col-lg-4 col-sm-4")
            p = tags.p(style="margin:0;")
            p.add(tags.input_(type="checkbox", name=f"{i}", id=f"{device}{i}"))
            p.add(tags.b(f"{device}{i}"))
            p.add(f" - {profile.device_name()}")
            curr_div.add(p)

    def checkboxes(
            self,
            device: str,
            support_groups: List[SupportGroup],
            profiles: List[Profile]):
        """
        Create checkboxes for given device profiles, optionally can
        specify support groups for additional buttons
        """
        with tags.div(className="row", id="grpChkBox"):
            with tags.div(className="btn-group", role="group"):
                self.checkbox_buttons(device, support_groups, profiles)
            self.checkbox_items(
                device,
                profiles,
            )

    def category(self, name: str, device: str, profiles, rows: Callable):
        """Function to create category section in table"""
        with tags.tr():
            tags.td(name, className="dark")
            # TODO Introduced in JC ver. xxx column
            for i, profile in enumerate(profiles):
                tags.th(
                    f"{device}{i}",
                    className=f"dark_index {i}",
                    title=profile.device_name()
                )
        rows()

    def basic_info_rows(self, basic_info_items, profiles, get_info):
        for item in basic_info_items:
            with tags.tr():
                tags.td(
                    item,
                    className="light"
                )
                for profile in profiles:
                    content = get_info(profile, item)
                    content = content.strip(";") if content else "-"
                    colored_cell(
                        partial(
                            tags.td,
                            title=f"{profile.device_name()} : {item} : {content}"
                        ),
                        content
                    )

    def table_header(
            self,
            device: str,
            basic_info_items: List[str],
            profiles: List[Profile],
            get_info: Callable):
        with tags.thead():
            self.category(
                name="Basic info",
                device=device,
                profiles=profiles,
                rows=partial(
                    self.basic_info_rows,
                    basic_info_items,
                    profiles,
                    get_info
                ),
            )

    def main_rows(
            self,
            all_keys: Set[str],
            profiles: List[Profile],
            get_content: Callable):
        for key in sorted(all_keys):
            with tags.tr():
                tags.td(key, className="light")
                for profile in profiles:
                    content = get_content(profile, key)
                    support = content.split(";")[0] if content else "-"
                    status = content.split(';')[1] if support == 'error' else support
                    colored_cell(
                        partial(
                            tags.td,
                            title=f"{profile.device_name()} : {key} : {status}"
                        ),
                        support
                    )

    def run_single(
            self,
            title: str,
            intro: Callable,
            abbreviations: Callable,
            notes: Optional[Callable],
            checkboxes: Callable,
            table: Callable,
            notebook: bool = False,
            device: str = 'javacard'
    ):
        doc_title = title

        additions = [
            AssetsPaths.SUPPORTTABLE_CSS,
            AssetsPaths.CHECKBOXES_JS
        ]

        def children_outside():
            with tags.div(className="container-fluid pt-5"):
                with tags.div(className="flex row pt-5"):
                    intro()
                abbreviations()
                if notes:
                    notes()
                checkboxes()
                with tags.b():
                    table()

        return layout(
            doc_title=doc_title,
            asset_additions=additions,
            children_outside=children_outside,
            back_to_top=True,
            notebook=notebook,
            device=device
        )


class SupportJC(Support, Page):
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
                "The table provides a list of algorithms defined in JavaCard "
                "API and supported by the particular smart card. The supported"
                " lengths of cryptographic keys, information about available "
                "RAM and EEPROM memory and garbage collection capabilities are"
                " also included."
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
                "JCAlgTest tool allows you to enumerate the supported "
                "cryptographic algorithms specified in JavaCard 3.0.5 and "
                "earlier. This page summarizes results obtained for cards "
                "available in our CRoCS laboratory and also results "
                "contributed by the community "
            )
            p.add(tags.b("(Many thanks folks!)"))
            p.add(tags.br())
            # Add credits for card result donors
            for name, value in self.get_donors().items():
                name = name.lstrip("(provided by ")
                name = name.rstrip(")")
                p.add(f"{name} ({value}x), ")
            tags.p(
                "The basic idea is simple - if the particular algorithm/key "
                "size is supported, then algorithm instance creation should "
                "succeed. Otherwise, CryptoException.NO_SUCH_ALGORITHM is "
                "thrown. Such a behavior can be employed for a quick test of "
                "supported algorithms. AlgTest applet tries to create an "
                "instance of an algorithm for all possible constants defined "
                "in JavaCard specification and eventually catch the exception."
                " JCAlgTest tool also tests additional tweaks like the "
                "possibility to use raw RSA for fast modular multiplication "
                "(which is usable to implement classical Diffie-Hellman key "
                "exchange) or manufacturer pre-set default "
                "ECC curve for ECC key pair."
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
        tags.h3("Tested card abbreviations")
        for i, profile in enumerate(self.profiles):
            tags.b(f"c{i}")
            tags.a(
                profile.test_info["Card name"],
                href=profile.test_info["Github link"]
            )
            tags.span(f", ATR={profile.test_info['Card ATR']}")
            tags.span(profile.test_info["Provider"])
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

    def jc_system(self):
        self.category(
            name="javacard.framework.JCSystem",
            device="card",
            profiles=self.profiles,
            rows=partial(
                self.main_rows,
                all_keys=set([
                    key for profile in self.profiles
                    for key in profile.jcsystem.keys()
                ]),
                profiles=self.profiles,
                get_content=lambda profile, key: profile.jcsystem.get(key),
            ),
        )

    def javacard_main(self):
        def get_content(profile, key):
            result = profile.results.get(key)
            if result:
                return ("yes" if result.support else "no") \
                    if result.status == "OK" else f"error;{result.status}"
            return "-"

        for cat in SupportJC.CATEGORIES:
            self.category(
                name=cat,
                device="card",
                profiles=self.profiles,
                rows=partial(
                    self.main_rows,
                    all_keys=set([
                        key for profile in self.profiles
                        for key, _ in list(filter(
                            lambda x: x[1].category == cat,
                            profile.results.items()
                        ))
                    ]),
                    profiles=self.profiles,
                    get_content=get_content,
                ),
            )

    def table(self):
        with tags.table(
                id="tab",
                width="37rem",
                border="0",
                cellspacing="2",
                cellpadding="4",
                className="table"
        ):
            self.table_header(
                device="card",
                basic_info_items=[
                    "AlgTest applet version", "JavaCard support version"
                ],
                profiles=self.profiles,
                get_info=lambda profile, key: profile.test_info.get(key)
            )
            with tags.tbody():
                self.jc_system()
                self.javacard_main()

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        html = self.run_single(
            title="JCAlgTest - Support table",
            intro=self.intro,
            abbreviations=self.abbreviations,
            notes=self.notes,
            checkboxes=partial(
                self.checkboxes,
                device="card",
                support_groups=SupportGroups.GROUPS,
                profiles=self.profiles,
            ),
            table=self.table,
            notebook=notebook
        )

        if output_path:
            output_path = f"{output_path}/{SupportJC.FILENAME}"
            with open(output_path, "w") as f:
                f.write(html)

        return html, output_path


class SupportTPM(Support, Page):
    FILENAME = "tpmtable.html"
    CATEGORIES = [
        "Quicktest_properties-fixed",
        "Quicktest_algorithms",
        "Quicktest_commands",
        "Quicktest_ecc-curves"
    ]

    def __init__(self, profiles):
        self.profiles: List[ProfileSupportTPM] = profiles

    def intro(self):
        with tags.div(className="col-xl-9"):
            tags.h1("List of supported TPM algorithms")

    def abbreviations(self):
        tags.h3("Tested TPM abbreviations")
        for i, profile in enumerate(self.profiles):
            tags.b(f"tpm{i}")
            tags.span(profile.test_info["TPM name"])
            tags.br()

    def tpm_main(self):
        def get_content(profile, key):
            properties = key not in TPM2Identifier.ALL_KEYS
            result = profile.results.get(key)
            if result:
                if result.value:
                    return result.value \
                        if not re.match(r"0x[0-9a-f]+", result.value) \
                        else str(int(result.value, 16))
                return "yes"
            return "-" if properties else "no"

        for cat in SupportTPM.CATEGORIES:
            self.category(
                name=cat,
                device="tpm",
                profiles=self.profiles,
                rows=partial(
                    self.main_rows,
                    all_keys=set([
                        key for profile in self.profiles
                        for key, _ in list(filter(
                            lambda x: x[1].category == cat,
                            profile.results.items()
                        ))
                    ]),
                    profiles=self.profiles,
                    get_content=get_content,
                ),
            )

    def table(self):
        with tags.table(
                id="tab",
                width="37rem",
                border="0",
                cellspacing="2",
                cellpadding="4",
                className="table"
        ):
            self.table_header(
                device="card",
                basic_info_items=["Image tag"],
                profiles=self.profiles,
                get_info=lambda profile, key: profile.test_info.get(key)
            )
            with tags.tbody():
                self.tpm_main()

    @overrides
    def run(self, output_path: Optional[str] = None, notebook: bool = False):
        html = self.run_single(
            title="tpm-algtest - Support table",
            intro=self.intro,
            abbreviations=self.abbreviations,
            notes=None,
            checkboxes=partial(
                self.checkboxes,
                device="tpm",
                support_groups={},
                profiles=self.profiles,
            ),
            table=self.table,
            notebook=notebook,
            device='tpm'
        )

        if output_path:
            output_path = f"{output_path}/{SupportTPM.FILENAME}"
            with open(output_path, "w") as f:
                f.write(html)

        return html, output_path
