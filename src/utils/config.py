import os
from functools import cached_property
import yaml
import collections.abc
from utils.models.config import Config

class ConfigException(Exception): ...

def get_config(config: str, root_auth_keys: list, user_auth_keys: list) -> Config:
    if config == 'nuc':
        from utils.configs.nuc import NucConfig
        return NucConfig(root_auth_keys, user_auth_keys)
    elif config == 'thinkpad':
        from utils.configs.thinkpad import ThinkpadConfig
        return ThinkpadConfig(root_auth_keys, user_auth_keys)
    else:
        raise ConfigException(f'No config implemented for {config}')
