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

Creates several html outputs from the results. Time of processing varies.

```
Usage: process.py [OPTIONS] {javacard|tpm} {process|all|execution-time|compara
                  tive|radar|scalability|similarity|support|compare|heatmap|sp
                  ectrogram}...

Options:
  -L, --legacy                 Enables parsing legacy TPM profiles stored in
                               csv format.
  -i, --results-dir DIRECTORY  Path to folder with results root directory.
  -o, --output-dir DIRECTORY   Path to folder where you want output to be
                               stored.
  --help                       Show this message and exit.
```

## License

This project is licensed under [MIT License](./LICENSE) - see the LICENSE file for details


