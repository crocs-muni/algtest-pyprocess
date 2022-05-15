from typing import List, Tuple

from dominate import tags

JC_HI_BASIC = [
    ("index.html#about", "About"),
    ("table.html", "Support table"),
    ("contact.html", "Contact"),
]
JC_HI_DROPDOWN = [
    (
        "Performance testing",
        [
            ("latest-info.html", "Latest Info"),
            ("how-it-works.html", "How it works"),
            ("run_time/execution-time.html", "Algorithm execution time"),
            ("comparative-table.html", "Comparative table"),
            ("scalability/scalability.html", "Scalability graphs"),
            ("radar_graphs/radar-graphs.html", "Radar graphs"),
            ("similarity-table.html", "Performance similarity table"),
        ],
    ),
    (
        "Related work",
        [
            (
                "https://crocs.fi.muni.cz/doku.php?id=public:research:smartcard:javacardcompilation",
                "JavaCard applet development (pre-prepared Ubuntu image)",
            ),
            (
                "https://www.fi.muni.cz/~xsvenda/apduinspect.html",
                "PC/SC inspection and manipulation tool",
            ),
            (
                "https://www.fi.muni.cz/~xsvenda/jcalgs.html",
                "Cryptographic algorithms re-implementation for JavaCard",
            ),
        ],
    ),
]

TPM_HI_BASIC = [
    ("tpmtable.html", "Support table"),
]

TPM_HI_DROPDOWN = [
    ('Performance testing', [
        ('run-time-tpm/execution-time.html', 'Algorithm execution time'),
        ('radar-graphs-tpm/radar-graphs.html', 'Radar graphs'),
        ('similarity-table-tpm.html', 'Similarity table'),
        ('cryptoprops-rsa.html', 'RSA Crypto properties')
    ])
]

DropdownLabel = str
DropdownLink = Tuple[str, str]
Dropdown = Tuple[DropdownLabel, List[DropdownLink]]


def header_items_dropdown(
        dropdowns: List[Dropdown],
        path_prefix: str = "./",
):
    divide_at = "How it works"
    for (label, items) in dropdowns:
        curr_id = ("navbarItemDropdown" + label).replace(" ", "")
        with tags.li(className="nav-item dropdown"):
            tags.button(
                label,
                aria_expanded="false",
                data_bs_toggle="dropdown",
                id=curr_id,
                type="button",
                className="nav-link text-light btn dropdown-toggle px-2",
            )
            with tags.ul(className="dropdown-menu", aria_labelledby=curr_id):
                for (href, name) in items:
                    with tags.li():
                        tags.a(
                            name,
                            href=path_prefix + href,
                            className="dropdown-item",
                        )
                    if name == divide_at:
                        tags.li(className="dropdown-divider")
                        tags.li("Results", className="dropdown-header")


def header_items_basic(items: List[Tuple[str, str]], path_prefix: str = "./"):
    for (href, name) in items:
        with tags.li(className="nav-item px-2"):
            tags.a(
                name,
                href=path_prefix + href,
                className="nav-link text-light text-decoration-none",
            )


def header(path_prefix: str = "./", device: str = 'javacard'):
    with tags.nav(
            className="navbar navbar-inverse navbar-expand-lg fixed-top "
                      "navbar-light bg-dark px-4 vw-100"
    ):
        if device == 'javacard':
            with tags.a(
                    className="navbar-brand", href=path_prefix + "/index.html"
            ):
                tags.img(src=path_prefix + "pics/logo_wide.png")

        with tags.button(
                className="navbar-toggler",
                type="button",
                data_bs_toggle="collapse",
                data_bs_target="#navbarContents",
                aria_controls="navbarContents",
                aria_expanded="false",
                aria_label="Toggle navigation",
        ):
            tags.span(className="navbar-toggler-icon")

        with tags.div(
                className="collapse navbar-collapse flex flex-row-reverse",
                id="navbarContents",
        ):
            with tags.ul(className="nav navbar-nav"):
                if device == 'javacard':
                    header_items_basic(JC_HI_BASIC[:2], path_prefix)
                    header_items_dropdown(JC_HI_DROPDOWN, path_prefix)
                    header_items_basic(JC_HI_BASIC[2:], path_prefix)
                elif device == 'tpm':
                    header_items_basic(TPM_HI_BASIC, path_prefix)
                    header_items_dropdown(TPM_HI_DROPDOWN, path_prefix)

