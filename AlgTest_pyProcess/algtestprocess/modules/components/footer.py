from functools import partial

from dominate import tags


def footer(path_prefix="./"):
    """
    Creates required script tags, back-to-top button
    """
    scripts = [
        (
            "text/javascript",
            "https://code.jquery.com/jquery-3.6.0.min.js",
            "sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=",
            "anonymous"
        ),
        (
            "text/javascript",
            f"{path_prefix}/footer.js",
            None,
            None
        ),
        (
            "text/javascript",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
            "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
            "anonymous"
        ),
        (
            "text/javascript",
            f"{path_prefix}/assets/js/ie10-viewport-bug-workaround.js",
            None,
            None
        ),
        (
            "text/javascript",
            "https://cdn.datatables.net/1.11.4/js/jquery.dataTables.min.js",
            None,
            None
        ),
        (
            "text/javascript",
            "https://cdn.datatables.net/1.11.4/js/dataTables.bootstrap5.min.js",
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
