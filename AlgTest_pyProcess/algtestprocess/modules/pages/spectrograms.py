import os

from dominate import tags
from typing import Dict, Tuple, List


from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.modal import modal, modal_script
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.visualization.spectrogram import Spectrogram
from algtestprocess.modules.visualization.utils import merge_cryptoprops_dfs


class Spectrograms(Page):
    FILENAME = "cryptoprops-ecc-nonce.html"
    SUBFOLDER_NAME = "spectrograms"
    ALGS = [
        "ecc_p256_ecdsa",
        "ecc_p256_ecdaa",
        "ecc_p256_ecschnorr",
        "ecc_p384_ecdsa",
        "ecc_p384_ecdaa",
        "ecc_p384_ecschnorr",
        "ecc_bn256_ecdsa",
        "ecc_bn256_ecdaa",
        "ecc_bn256_ecschnorr",
    ]

    def __init__(self, profiles):
        self.profiles = profiles
        # Custom y axis scaling depending on algorithm
        self.yminymax: Dict[str, Tuple[int, int]] = {}
        # Custom precision depending on algoritm
        self.precision: Dict[str, float] = {
            "ecc_p256_ecdsa": 3,
            "ecc_bn256_ecdaa": 3,
            "default": 2,
        }

    def columns(self, n: int, items):
        cols = [tags.div(className="col-sm") for _ in range(n)]
        for i, item in enumerate(items):
            cols[i % n].add(item)

    def _get_sections(self, output_path, algs, items):
        sections = {alg: [] for alg in algs}
        # Then we create svg spectrograms from those results where datasets are ok
        for i, (df, device_name, alg) in enumerate(items):
            # If errorneous dataset, skip
            if device_name is None:
                continue

            try:
                precision = (
                    self.precision[alg]
                    if alg in self.precision
                    else self.precision["default"]
                )
                filename = f"{i}_{device_name.replace(' ', '_')}_{alg}.png"

                print(self.yminymax[alg])

                Spectrogram(
                    df, device_name, precision=precision, yrange=self.yminymax[alg]
                ).build().save(
                    filename=f"{output_path}/{Spectrograms.SUBFOLDER_NAME}/{filename}"
                )
            except (TypeError, AttributeError) as ex:
                print(ex)
                continue
            sections[alg].append(filename)

        return sections

    def set_uniform_yminymax(self, algs: List[str], items):
        self.yminymax = {
            alg: (
                min(
                    [
                        df.duration.nsmallest(5).max()
                        for df, _, algorithm in items
                        if algorithm == alg and df is not None
                    ]
                ),
                max(
                    [
                        df.duration.nlargest(5).min()
                        for df, _, algorithm in items
                        if algorithm == alg and df is not None
                    ]
                ),
            )
            for alg in algs
        }

    def run(self, output_path: str, notebook=False):
        algs = Spectrograms.ALGS

        items_base, items_merged = merge_cryptoprops_dfs(self.profiles, algs)

        # Create subfolder if it does not exist
        path = f"{output_path}/{Spectrograms.SUBFOLDER_NAME}"
        if not os.path.exists(path):
            os.mkdir(path)

        # self.set_uniform_yminymax(algs, items_base)
        # sections_base = self._get_sections(output_path, algs, items_base)

        self.set_uniform_yminymax(algs, items_merged)
        sections_merged = self._get_sections(output_path, algs, items_merged)

        n = 4
        # Create img tag for each created spectrogram
        create_img_tags = lambda filenames: list(
            map(
                lambda filename: tags.a(
                    tags.img(
                        src=f"./{Spectrograms.SUBFOLDER_NAME}/{filename}",
                        className="img-responsive",
                        style="width: 100%; height: auto;",
                    ),
                    href="#",
                    className="pop",
                ),
                filenames,
            )
        )

        # sections_base = [
        #    (alg, create_img_tags(filenames))
        #    for alg, filenames in sections_base.items()
        # ]

        sections_merged = [
            (alg, create_img_tags(filenames))
            for alg, filenames in sections_merged.items()
        ]

        def children():
            tags.h1(
                "Cryptographic properties of TPM generated ECC signatures keys",
                className="pt-5",
            )
            for sections, name in [
                (sections_merged, "Merged"),
                #        (sections_base, "Base"),
            ]:
                tags.h2(name, className="pt-2")
                for alg, img_tags in sections:
                    tags.h3(alg.replace("_", " "), className="pt-5")
                    with tags.div(className="row"):
                        self.columns(n, img_tags)

        def children_outside():
            modal()
            modal_script()

        html = layout(
            doc_title="Cryptographic properties of TPM generated ECC nonces",
            children=children,
            notebook=notebook,
            children_outside=children_outside,
            device="tpm",
        )

        with open(f"{output_path}/{Spectrograms.FILENAME}", "w") as f:
            f.write(html)
