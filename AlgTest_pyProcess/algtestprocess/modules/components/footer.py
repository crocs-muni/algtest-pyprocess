from functools import partial
from typing import List

from dominate import tags

from algtestprocess.modules.components.utils import AssetsPaths, inline_assets


def footer(additions: List[str], path_prefix="./",  inline:bool = False):
    """
    Either creates required script tags, or inlines the JavaScript
    """
    if inline:
        paths = [
            f"./{AssetsPaths.JQUERY_JS}",
            f"./{AssetsPaths.BOOTSTRAP_JS}",
            f"./{AssetsPaths.VIEWPORT_JS}",
            f"./{AssetsPaths.JQUERY_DATATABLES_JS}",
            f"./{AssetsPaths.DATATABLES_BS_JS}"
        ] + [f"./{add}" for add in additions if "js" in add]
        inline_assets(paths)
        return

    scripts = [
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.JQUERY_JS}",
            None,
            None
        ),
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.LICENSE_JS}",
            None,
            None
        ),
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.BOOTSTRAP_JS}",
            None,
            None
        ),
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.VIEWPORT_JS}",
            None,
            None
        ),
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.JQUERY_DATATABLES_JS}",
            None,
            None
        ),
        (
            "text/javascript",
            f"{path_prefix}/{AssetsPaths.DATATABLES_BS_JS}",
            None,
            None
        )
    ]

    tags.a(href="#", className="back-to-top")

    # Create each script tag procedurally, because undefined attributes don't
    # work in HTML
    for script in scripts:
        type_, src, integrity, crossorigin = script
        tag = tags.script
        if type_:
            tag = partial(tag, type=type_)
        if src:
            tag = partial(tag, src=src)
        if integrity:
            tag = partial(tag, integrity=integrity)
        if crossorigin:
            tag = partial(tag, crossorigin=crossorigin)
        tag()
