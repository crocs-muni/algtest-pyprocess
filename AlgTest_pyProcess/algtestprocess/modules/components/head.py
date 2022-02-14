from dominate import tags


def head(path_prefix="./"):
    """Common <head> for generated pages"""
    with tags.head():
        tags.meta(charset="utf-8")
        tags.meta(http_equiv="X-UA-Compatible", content="IE=edge")
        tags.meta(
            name="viewport", content="width=device-width, initial-scale=1"
        )
        tags.meta(
            name="description",
            content="The JCAlgTest is a tool designed for automatic "
                    "gathering various performance properties of Java cards.",
        )
        tags.meta(name="author", content="JCAlgTest")
        # TODO: switch for local css loading
        tags.link(
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
            rel="stylesheet",
            integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
            crossorigin="anonymous",
        )
        tags.link(
            rel="stylesheet",
            type="text/css",
            href=path_prefix + "dist/style.css",
        )
        tags.script(
            src="https://code.jquery.com/jquery-3.6.0.min.js",
            integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=",
            crossorigin="anonymous",
        )
