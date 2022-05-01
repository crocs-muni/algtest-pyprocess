import pandas as pd


class Detail:

    def __init__(self, path: str):
        self.path = f"{path}/tpm/profiles/detail"

    def parse(self):
        rsa_1024 = pd.read_csv(
            f"{self.path}/Keygen:RSA_1024.csv",
            header=0,
            delimiter=";"
        )
        rsa_2048 = pd.read_csv(
            f"{self.path}/Keygen:RSA_2048.csv",
            header=0,
            delimiter=";"
        )
        output = {
            "rsa_1024": rsa_1024,
            "rsa_2048": rsa_2048
        }
        return output

