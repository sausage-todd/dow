import os
import tomllib

import tomli_w

from dow.config.data import Config


def __config_path() -> str:
    return os.path.expanduser("~/.config/dow/config.toml")


def read() -> Config:
    config_path = __config_path()
    if not os.path.exists(config_path):
        return Config.empty()

    with open(config_path, "rb") as f:
        return Config.parse_obj(tomllib.load(f))


def write(data: Config):
    config_path = __config_path()
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    with open(config_path, "wb") as out:
        tomli_w.dump(data.dict(), out)
