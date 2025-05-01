from utils.models.config import Config


class WyseConfig(Config):
    def __init__(self, root_auth_keys: list, user_auth_keys: list):
        super().__init__(root_auth_keys, user_auth_keys)
        self.hostname = "vehuiah"
