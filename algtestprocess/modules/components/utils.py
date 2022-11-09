import sys
from typing import List

from dominate import tags
from dominate.util import  raw


class AssetsPaths:
    BOOTSTRAP_CSS = "assets/css/bootstrap.min.css"
    SUPPORTTABLE_CSS = "assets/css/supporttable_style.css"
    STYLE_CSS = "assets/css/style.css"
    BOOTSTRAP_JS = "assets/js/bootstrap.bundle.min.js"
    JQUERY_JS = "assets/js/jquery-3.6.0.min.js"
    JQUERY_DATATABLES_JS = "assets/js/jquery.dataTables.min.js"
    DATATABLES_BS_JS = "assets/js/dataTables.bootstrap5.min.js"
    LICENSE_JS = "assets/js/license.js"
    VIEWPORT_JS = "assets/js/ie10-viewport-bug-workaround.js"
    D3_JS = "assets/js/d3.v3.min.js"
    RADAR_JS = "assets/js/RadarChart.js"
    CHECKBOXES_JS = "assets/js/checkboxes.js"


def get_assets(paths: List[str]):
    out = []
    for path in paths:
        try:
            with open(path, "r") as f:
                data = f.read()

            if "css" in path:
                out.append(("css", data))
            elif "js" in path:
                out.append(("js", data))

        except Exception as ex:
            print("Please ensure assets directory is in the same folder "
                  "from where you executed the script")
            print(ex)
            sys.exit(1)
    return out


def inline_assets(paths):
    data = get_assets(paths)
    for filetype, content in data:
        if filetype == "css":
            tags.style(raw(content))
        elif filetype == "js":
            tags.script(raw(content), type="text/javascript")
