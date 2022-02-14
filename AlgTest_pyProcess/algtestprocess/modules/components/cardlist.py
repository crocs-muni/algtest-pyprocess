from typing import List, Tuple, Callable, Optional

from dominate import tags

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.pages.utils import Name, Href


def cardlist(
        data: List[Tuple[Name, Href]],
        title: str,
        text: Callable,
        img: Callable,
        alert: Optional[Callable],
):
    """
    Page for referencing each card created
    """

    def children():
        with tags.div(className="row pt-5"):
            with tags.div(className="col-md-7 col-xs-7"):
                text()
            with tags.div(className="col-md-5 col-xs-5 overflow-hidden"):
                img()
            if alert:
                alert()
        tags.h4("List of tested Java Cards")
        with tags.ul(className="list-group"):
            for name, href in data:
                with tags.li(className="list-group-item"):
                    tags.a(
                        name, href=href, className="text-decoration-none"
                    )

    return layout(
        doc_title=title,
        children=children,
        path_prefix="../",
        back_to_top=True
    )
