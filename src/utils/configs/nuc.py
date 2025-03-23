from utils.models.config import Config

class NucConfig(Config):
    def __init__(self, root_auth_keys: list, user_auth_keys: list):
        super().__init__(self, root_auth_keys, user_auth_keys)
        self.hostname = 'nuc'
        self.debug = True

        self.network.ethernet_interface_id = 'enp3s0'
