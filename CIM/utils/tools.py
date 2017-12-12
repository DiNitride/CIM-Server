from os import getenv, getcwd
import pathlib
import json


def load_config(filename: str):
    base = getenv("CONFIG_BASE", getenv("CIM_ROOT") + "/config")

    with open(pathlib.Path(base, filename)) as fp:
        return json.load(fp)
