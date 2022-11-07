import os

from dominate import tags
from tqdm import tqdm

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.modal import modal, modal_script
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.visualization.heatmap import Heatmap


class Heatmaps(Page):
    FILENAME = "cryptoprops-rsa.html"
    SUBFOLDER_NAME = "heatmaps"

    def __init__(self, profiles):
        self.profiles = profiles

    def columns(self, n: int, items):
        cols = [tags.div(className="col-sm") for _ in range(n)]
        for i, item in enumerate(items):
            cols[i % n].add(item)

    def run(self, output_path: str, notebook=False):
        # First we need the profiles which have rsa data
        filtered_1024 = list(
            map(
                lambda profile: (profile["rsa_1024"], profile["device_name"]),
                filter(
                    lambda profile: profile.get("rsa_1024") is not None, self.profiles
                ),
            )
        )
        filtered_2048 = list(
            map(
                lambda profile: (profile["rsa_2048"], profile["device_name"]),
                filter(
                    lambda profile: profile.get("rsa_2048") is not None, self.profiles
                ),
            )
        )

        # Create subfolder if it does not exist
        path = f"{output_path}/{Heatmaps.SUBFOLDER_NAME}"
        if not os.path.exists(path):
            os.mkdir(path)

        # Then we create svg heatmaps from those results where datasets are ok
        heatmaps_1024 = []
        heatmaps_2048 = []
        items = [
            (heatmaps_1024, filtered_1024, "1024"),
            (heatmaps_2048, filtered_2048, "2048"),
        ]
        for heatmaps, filtered, bits in items:
            for i in tqdm(range(len(filtered)), desc=f"RSA {bits} Heatmaps"):
                items = filtered[i]
                df, device_name = items
                try:
                    # If errorneous dataset, skip
                    name = f"{i}-{device_name.replace(' ', '_')}-RSA{bits}.png"
                    Heatmap(df, device_name).save(
                        filename=f"{output_path}/{Heatmaps.SUBFOLDER_NAME}/{name}"
                    )
                except TypeError:
                    continue
                heatmaps.append((device_name, name))
            heatmaps.sort(key=lambda item: item[0])

        n = 4
        # Create img tag for each created heatmap
        heatmaps_1024 = list(
            map(
                lambda item: tags.a(
                    tags.img(
                        src=f"./{Heatmaps.SUBFOLDER_NAME}/{item[1]}",
                        className="img-responsive",
                        style=f"width: 100%; height: auto;",
                    ),
                    href="#",
                    className="pop",
                ),
                heatmaps_1024,
            )
        )
        heatmaps_2048 = list(
            map(
                lambda item: tags.a(
                    tags.img(
                        src=f"./{Heatmaps.SUBFOLDER_NAME}/{item[1]}",
                        classname="img-responsive",
                        style=f"width: 100%; height: auto;",
                    ),
                    href="#",
                    className="pop",
                ),
                heatmaps_2048,
            )
        )

        def children():
            tags.h1(
                "Cryptographic properties of TPM generated RSA keys", className="pt-5"
            )
            tags.h2("RSA 1024", className="pt-5")
            with tags.div(className="row"):
                self.columns(n, heatmaps_1024)
            tags.h2("RSA 2048", className="pt-5")
            with tags.div(className="row"):
                self.columns(n, heatmaps_2048)

        def children_outside():
            modal()
            modal_script()

        html = layout(
            doc_title="Cryptographic properties of TPM generated RSA keys",
            children=children,
            notebook=notebook,
            children_outside=children_outside,
            device="tpm",
        )

        with open(f"{output_path}/{Heatmaps.FILENAME}", "w") as f:
            f.write(html)
