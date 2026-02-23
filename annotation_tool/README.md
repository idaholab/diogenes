# Diogenes Annotation Tool

This tool is designed to make it easier to create annotation files for the Diogenes process.

## Requirements

This tool is made to run in Python 3.9 (or above), and is managed with [uv](https://docs.astral.sh/uv/).

`uv` is pretty cool, and I'd reccomend it, but if you wish to install the depenancies manually they are:

- `pandas`
- `xlsxwriter`

In addition, if you wish to use the ML Model, it requires `scikit-learn`, but this is optional.

## Instructions

You can run this tool by calling `python main.py [Input Data Directory]`, but if you use `uv run main.py [Input Data Directory]`, `uv` will automatically install all the required stuff for you.

There are additional flags you can discover with the `-h` or `--help` flag. They are not required.

## Agents

Two Agents are included at the moment: `tree` and `ml_tree`.

`tree` is a manually created decision tree, while `ml_tree` is a machine learning model trained on TSDC data. `ml_tree` tends to perform about twice as well as `tree`, but it is more aggressive, and thereby may make more incorrect annotations depending on the data. 
