from typing import List, Optional

from dominate import tags


def simple_table(
    data: List[List[Optional[str]]],
    table_header: Optional[List[str]] = None,
    table_cls: str = "",
    table_id: str = "",
    th_cls: str = "",
):
    """Table generation procedure"""
    with tags.table(
        className="table table-bordered table-hover " + table_cls, id=table_id
    ):
        if not table_header:
            table_header = []

        if table_header:
            with tags.thead():
                with tags.tr():
                    for cell in table_header:
                        tags.th(cell, className="col " + th_cls)

        with tags.tbody():
            for trow in data:
                with tags.tr():
                    for i in range(len(trow)):
                        col_span = 1
                        # Last cell to fill all cols left
                        if i == len(trow) - 1 and len(trow) < len(
                            table_header
                        ):
                            col_span = len(table_header) - len(trow) + 1
                        tags.td(
                            trow[i] if trow[i] else "-",
                            className="border-top border-bottom",
                            colspan=col_span,
                        )
