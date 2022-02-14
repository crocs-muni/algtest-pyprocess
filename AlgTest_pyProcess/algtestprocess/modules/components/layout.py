from typing import Callable, Optional

from dominate import document, tags

from algtestprocess.modules.components.footer import footer
from algtestprocess.modules.components.head import head
from algtestprocess.modules.components.header import header


def layout(
        doc_title: str,
        children: Optional[Callable] = None,
        children_outside: Optional[Callable] = None,
        head_additions: Optional[Callable] = None,
        back_to_top: bool = False,
        path_prefix: str = './'
):
    doc = document(title=doc_title)
    with doc.head:
        head()
        if head_additions:
            head_additions()
    with doc:
        header(path_prefix=path_prefix)
        if children:
            with tags.div(className="container pt-5"):
                children()
        if children_outside:
            children_outside()
        if back_to_top:
            tags.a(href="#", className="back-to-top")
        footer(path_prefix=path_prefix)
    return str(doc)
