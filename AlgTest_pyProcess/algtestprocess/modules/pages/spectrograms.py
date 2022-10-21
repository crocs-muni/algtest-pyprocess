import os

from dominate import tags

import pandas as pd

from algtestprocess.modules.components.layout import layout
from algtestprocess.modules.components.modal import modal, modal_script
from algtestprocess.modules.pages.page import Page
from algtestprocess.modules.visualization.spectrogram import Spectrogram


class Spectrograms(Page):
    FILENAME = "cryptoprops-ecc-nonce.html"
    SUBFOLDER_NAME = "spectrograms"

    def __init__(self, profiles):
        self.profiles = profiles

    def columns(self, n: int, items):
        cols = [tags.div(className="col-sm") for _ in range(n)]
        for i, item in enumerate(items):
            cols[i % n].add(item)

    def _get_sections(self, output_path, algs, items):
        sections = {alg: [] for alg in algs}
        # Then we create svg spectrograms from those results where datasets are ok
        for i, (df, device_name, alg) in enumerate(items):
            if device_name is None:
                continue

            try:
                # If errorneous dataset, skip
                filename = f"{i}_{device_name.replace(' ', '_')}_{alg}.png"
                Spectrogram(
                    df,
                    device_name).build().save(
                    filename=f"{output_path}/{Spectrograms.SUBFOLDER_NAME}/{filename}"
                )
            except (TypeError, AttributeError):
                continue
            sections[alg].append(filename)

        return sections


    def run(self, output_path: str, notebook=False):
        algs = [
            'ecc_p256_ecdsa',
            'ecc_p256_ecdaa',
            'ecc_p256_ecschnorr',
            'ecc_p384_ecdsa',
            'ecc_p384_ecdaa',
            'ecc_p384_ecschnorr',
            'ecc_bn256_ecdsa',
            'ecc_bn256_ecdaa',
            'ecc_bn256_ecschnorr'
        ]
        items_base = [
            (profile.get(alg), profile.get('device_name'), alg)
            for alg in algs for profile in self.profiles
        ]

        items_merged = {}
        for alg in algs:
            items_by_alg = [item for item in items_base if item[2] == alg]
            for df, device_name, _ in items_by_alg:
                key = (device_name, alg)
                items_merged.setdefault(key, [])
                if df is not None:
                    items_merged[key].append(df)
        items_merged = [
            (pd.concat(dfs), f"{device_name} MERGED", alg)
            for (device_name, alg), dfs in items_merged.items()
            # Only show if there are multiple measurements for same
            # device, otherwise dont
            if len(dfs) > 1
        ]

        # Create subfolder if it does not exist
        path = f"{output_path}/{Spectrograms.SUBFOLDER_NAME}"
        if not os.path.exists(path):
            os.mkdir(path)

        sections_base = self._get_sections(output_path, algs, items_base)
        sections_merged = self._get_sections(output_path, algs, items_merged)


        n = 4
        # Create img tag for each created spectrogram
        create_img_tags = lambda filenames: list(map(lambda filename: tags.a(
            tags.img(
                src=f"./{Spectrograms.SUBFOLDER_NAME}/{filename}",
                className="img-responsive",
                style="width: 100%; height: auto;"
            ),
            href="#",
            className="pop"
        ), filenames))

        sections_base = [
            (alg, create_img_tags(filenames)) for alg, filenames in sections_base.items()
        ]

        sections_merged = [
            (alg, create_img_tags(filenames)) for alg, filenames in sections_merged.items()
        ]

        def children():
            tags.h1(
                "Cryptographic properties of TPM generated ECC signatures keys",
                className="pt-5"
            )
            for sections, name in [(sections_merged, 'Merged'), (sections_base, 'Base')]:
                tags.h2(name, className="pt-2")
                for alg, img_tags in sections:
                    tags.h3(alg.replace('_', ' '), className="pt-5")
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
            device='tpm'
        )

        with open(f"{output_path}/{Spectrograms.FILENAME}", "w") as f:
            f.write(html)
