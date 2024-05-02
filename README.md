# `conntrack-to-csv`

Turn `conntrack -L` output into a CSV.

This is useful when you want to import your conntrack entries into a spreadsheet.

## Requirements

You just need `python3` and `pip3`.

```sh
$ python3 --version
Python 3.11.0

$ pip3 --version
pip 22.3 from ./conntrack-to-csv/venv/Lib/site-packages/pip (python 3.11)
```

## Installation

Just clone this project and Install the requirements with `pip3`.

```sh
# Clone this project
$ git clone git@github.com:penafieljlm/conntrack-to-csv.git

# Navigate into the project
$ cd conntrack-to-csv

# Install the requirements
$ pip3 install -r requirements.txt
```

## Usage

The following snippet describes how to use the script.

```sh
$ python3 conntrack-to-csv.py3 -h
usage: conntrack-to-csv.py3 [-h] input output

positional arguments:
  input       Input file path
  output      Output file path

options:
  -h, --help  show this help message and exit
```

Typical use-case is as follows:

```sh
# Dump conntrack entries into a file
$ conntrack -L > conntrack.txt

# Convert conntrack entries file into a CSV file
$ python3 conntrack-to-csv.py3 conntrack.txt conntrack.csv
```

You can read from `stdin` by specifying `-` as the input file path:

```sh
$ conntrack -L | python3 conntrack-to-csv.py3 - conntrack.csv
```

You can write to `stdout` by specifying `-` as the output file path:

```sh
$ conntrack -L | python3 conntrack-to-csv.py3 - -
```

## Notes

To check syntax with `mypy`:

```sh
$ mypy conntrack-to-csv.py3
```

To automatically sort imports with `isort`:

```sh
$ isort conntrack-to-csv.py3
```
