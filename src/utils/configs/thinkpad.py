from utils.models.config import Config

class ThinkpadConfig(Config):
    def __init__(self, root_auth_keys: list, user_auth_keys: list):
        super().__init__(root_auth_keys, user_auth_keys)
        self.hostname = 'thinkpad'
        self.script['preseed'].additional_steps = [
            "echo 'HandleLidSwitch=ignore' >> /etc/systemd/logind.conf",
            "echo 'HandleLidSwitchDocked=ignore' >> /etc/systemd/logind.conf",
        ]

        self.network.ethernet_interface_id = 'enp0s25'
