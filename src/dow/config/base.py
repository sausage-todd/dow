import os
import tomllib

import tomli_w


def read() -> dict:
    config_path = os.path.expanduser("~/.config/dow/config.toml")
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def write(data: dict):
    config_path = os.path.expanduser("~/.config/dow/config.toml")
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    with open(config_path, "wb") as out:
        tomli_w.dump(data, out)
