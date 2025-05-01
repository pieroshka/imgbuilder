import os
from functools import cached_property
import yaml
import collections.abc
from utils.models.config import Config


class ConfigError(Exception): ...


def get_config(config: str, root_auth_keys: list, user_auth_keys: list) -> Config:
    match config:
        case "nuc":
            from utils.configs.nuc import NucConfig

            return NucConfig(root_auth_keys, user_auth_keys)
        case "thinkpad":
            from utils.configs.thinkpad import ThinkpadConfig

            return ThinkpadConfig(root_auth_keys, user_auth_keys)
        case "wyse":
            from utils.configs.wyse import WyseConfig

            return WyseConfig(root_auth_keys, user_auth_keys)
        case _:
            raise ConfigError(f"No config implemented for {config}")
