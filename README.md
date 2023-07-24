# Algtest pyProcess

A tool for simple visualizations of gathered TPM and JavaCard smart card data collected by tpm2-algtest and JCAlgtest tools respectively.

## Getting started

### Dependencies

* Python 3 (see. [requirements.txt](./requirements.txt))

### Installing

* Setup virtual environment, then run *setup.py*
```
python -m venv venv
source venv/bin/activate
python setup.py
```
---
**NOTE**

If you are an user of fish shell, right command is `source venv/bin/activate.fish`

---

### Usage

#### process.py script

An entry point to the command line interface, which consists of several scripts for processing datasets.

```
Commands:
  tpm       A collection of commands for processing of results from tpm2-algtest
  javacard  NOT YET IMPLEMENTED
```

##### tpm commands

###### metadata-update

Important command which goal is to find measurements on a given path, group them by exact firmware and output `metadata.json` file which is used as an input to other commands. It also prevents inclusion of exact same measurements more than once. An example of such file is shown below.

```
python process.py tpm metadata-update ./results/tpmalgtest_results_2022
python process.py tpm metadata-update -i metadata.json ./results/tpmalgtest_results_2023
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

##### report-create

Batch command which creates several kinds of outputs from the measurements noted in `metadata.json` created by `metadata-update` command. 


```
python process.py report-create metadata.json
```
## License

This project is licensed under [MIT License](./LICENSE) - see the LICENSE file for details


