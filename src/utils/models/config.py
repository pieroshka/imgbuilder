from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from passlib.hash import md5_crypt


@dataclass
class User:
    name: str = field(default="debian")
    password: str = field(default="debian")
    password_hash: Optional[str] = field(default=None, init=False)
    authorized_keys: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._update_password_hash()

    def _update_password_hash(self) -> str:
        self.password_hash = str(md5_crypt.hash(self.password))

    def set_password(self, password: str):
        self.password = password
        self._update_password_hash()


@dataclass
class Script:
    location: str = field(default="/")
    additional_steps: List[str] = field(default_factory=list)


@dataclass
class NetworkInterface:
    name: str = field(default="noname")
    creation_steps: List[str] = field(default_factory=list)


@dataclass
class NetworkConfig:
    interfaces: List[NetworkInterface] = field(default_factory=list)
    ethernet_interface_id: str = field(default="enp1s0")
    cidr_range: str = field(default="192.168.1.80/28")


@dataclass
class AptConfig:
    packages: List[str] = field(
        default_factory=lambda: [
            "openssh-server",
            "avahi-daemon",
            "sudo",
            "build-essential",
            "zlib1g-dev",
            "libncurses5-dev",
            "libgdbm-dev",
            "libnss3-dev",
            "libssl-dev",
            "libreadline-dev",
            "libffi-dev",
            "libsqlite3-dev",
            "wget",
            "libbz2-dev",
            "python3",
            "open-iscsi",  # longhorn dependency
            # "bridge-utils",
            # dev packages
            # secureboot packages # TODO
            # "ovmf",
            # "gpg",
            # "debian-keyring",
        ]
    )
    update: bool = field(default=True)
    upgrade: bool = field(default=True)


@dataclass
class Config:
    hostname: str = field(default="hostname")
    root_user: User = field(
        default_factory=lambda: User(
            name="root",
            password="root",
        )
    )
    users: List[User] = field(default_factory=lambda: [User()])
    script: Dict[str, Script] = field(
        default_factory=lambda: {
            "preseed": Script(location="/root/preseed-setup.sh"),
            "firstboot": Script(location="/root/firstboot-setup.sh"),
        }
    )
    network: NetworkConfig = field(default_factory=NetworkConfig)
    apt: AptConfig = field(default_factory=AptConfig)
    debug: bool = field(default=False)

    def __init__(self, root_auth_keys: list, user_auth_keys: list):
        self.hostname = "hostname"
        self.root_user = User(
            name="root", password="root", authorized_keys=root_auth_keys
        )
        self.users = [
            User(name="debian", password="debian", authorized_keys=user_auth_keys)
        ]
        self.script = {
            "preseed": Script(location="/root/preseed-setup.sh"),
            "firstboot": Script(location="/root/firstboot-setup.sh"),
        }
        self.network = NetworkConfig()
        self.apt = AptConfig()
        self.debug = False

    def as_dict(self) -> dict:
        return asdict(self)
