# Algtest pyProcess

A tool for simple visualizations of gathered TPM and JavaCard smart card data collected by tpm2-algtest and JCAlgtest tools respectively.

## Getting started

### Dependencies

* Python 3 (see. [requirements.txt](./requirements.txt))

### Installing

* Setup virtual environment
```
python -m venv venv
source venv/bin/activate
```

* Install package using `pip` or run `setup.py`
```
pip install -e .
```

---
**NOTE**

If you are an user of fish shell, right command is `source venv/bin/activate.fish`

---

### Usage

#### pyprocess command

An entry point to the command line interface, which is used mostly to preprocess the datasets which are then analysed in jupyter notebooks.

```
Commands:
  tpm       A collection of commands for processing of results from tpm2-algtest
  javacard  NOT YET IMPLEMENTED
```

##### tpm commands

###### metadata-update

Command which is used to find all measurements on a given path, and group them by exact firmware. The output is `metadata.json` which contains these aggregated paths. Latter part of this file contains directory hashes, to prevent duplicate inclusion of the same measurement. An example of `metadata.json` file is shown below.

If you have already created a `metadata.json` file and just want to add more measurements, you may use `-i` option which takes path to old `metadata.json` file.
```
pyprocess tpm metadata-update ./results/tpmalgtest_results_2022
pyprocess tpm metadata-update -i metadata.json ./results/tpmalgtest_results_2023
```

An example of `metadata.json` file.

```
{
  "entries": {
    "STM 73.4.17568.4452": {
      "TPM name": "STM 73.4.17568.4452",
      "vendor": "STM",
      "title": "",
      "measurement paths": [
        "/home/tjaros/storage/research/tpm/tpmalgtest_results/out4/out",
        "/home/tjaros/storage/research/tpm/tpmalgtest_results/algtest_result_8d400ec7-122c-498f-b141-733d359ad78f_STM",
        "/home/tjaros/storage/research/tpm/tpmalgtest_results/algtest_result_9fdfdf94-3a4a-4cd3-9a92-86642f9f4f6c"
      ]
    },
    "AMD AMD 3.37.0.5": {
      "TPM name": "AMD AMD 3.37.0.5",
      "vendor": "AMD",
      "title": "",
      "measurement paths": [
        "/home/tjaros/storage/research/tpm/tpmalgtest_results/algtest_result_70de7ce0-de7c-42bc-9f86-708d8304ad48"
      ]
    },
  },
   "hashes": [
    "862ad83383339467dbd687f3ebb2d075",
    "7f78e96bd4fc47299cdbaa7cf1a1c1e3",
    "3d6f2c211f00245d2a7b2c6458b3626a",
    "2b3242fc08c73b608a227eea563f1531",
   ],
}
```

## License

This project is licensed under [MIT License](./LICENSE) - see the LICENSE file for details


