from typing import Callable, Optional, List

from dominate import document, tags

from algtestprocess.modules.components.footer import footer
from algtestprocess.modules.components.head import head
from algtestprocess.modules.components.header import header


def layout(
        doc_title: str,
        children: Optional[Callable] = None,
        children_outside: Optional[Callable] = None,
        asset_additions: Optional[List[str]] = None,
        other_scripts: Optional[List[callable]] = None,
        back_to_top: bool = False,
        path_prefix: str = './',
        notebook: bool = False,
):
    doc = document(title=doc_title)
    with doc.head:
        head(
            path_prefix=path_prefix,
            additions=asset_additions if asset_additions else [],
            inline=notebook
        )
    with doc:
        if not notebook:
            header(path_prefix=path_prefix)
        if children:
            with tags.div(className="container pt-5"):
                children()
        if children_outside:
            children_outside()
        if not notebook:
            if back_to_top:
                tags.a(href="#", className="back-to-top")

        footer(
            path_prefix=path_prefix,
            additions=asset_additions if asset_additions else [],
            inline=notebook
        )

        if other_scripts:
            for script in other_scripts:
                script()
    return str(doc)
