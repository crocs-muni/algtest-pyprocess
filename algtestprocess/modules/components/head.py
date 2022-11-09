from typing import List

from dominate import tags

from algtestprocess.modules.components.utils import inline_assets, AssetsPaths


def head(additions: List[str], path_prefix="./", inline: bool = False):
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

        if not inline:
            tags.link(
                href=f"{path_prefix}/{AssetsPaths.BOOTSTRAP_CSS}",
                type="text/css",
                rel="stylesheet",
            )
            tags.link(
                rel="stylesheet",
                type="text/css",
                href=f"{path_prefix}/{AssetsPaths.STYLE_CSS}",
            )
            tags.script(
                src=f"{path_prefix}/{AssetsPaths.JQUERY_JS}",
                type="text/javascript"
            )
            for addition in additions:
                if "css" in addition:
                    tags.link(
                        rel="stylesheet",
                        type="text/css",
                        href=f"{path_prefix}/{addition}"
                    )
                elif "js" in addition:
                    tags.script(
                        src=f"{path_prefix}/{addition}",
                        type="text/javascript"
                    )

        else:
            paths = [
                f"./{AssetsPaths.BOOTSTRAP_CSS}",
                f"./{AssetsPaths.STYLE_CSS}",
            ] + [f"./{addition}" for addition in additions if "css" in addition]
            inline_assets(paths)


