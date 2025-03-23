from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from passlib.hash import md5_crypt

@dataclass
class User:
    name: str = field(default='debian')
    password: str = field(default='debian')
    password_hash: Optional[str] = field(default=None, init=False)
    libvirt_user: bool = field(default=True)
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
    location: str = field(default='/nonexistent/path')
    additional_steps: List[str] = field(default_factory=list)

@dataclass
class NetworkInterface:
    name: str = field(default='noname')
    creation_steps: List[str] = field(default_factory=list)

@dataclass
class NetworkConfig:
    interfaces: List[NetworkInterface] = field(default_factory=list)
    # ip_interfaces = List[NetworkInterface] = field(default_factory=lambda: [
    #     NetworkInterface('bridge0', creation_steps=[
    #         "ip link add name {{ network.bridge_name }} type bridge",
    #         "ip link set {{ network.ethernet_interface_id }} up",
    #         "ip link set {{ network.ethernet_interface_id }} master {{ network.bridge_name }}",
    #         # add static ip address to bridge
    #         "ip address add dev {{ network.bridge_name }} {{ network.cidr_range }}",
    #     ]),
    # ])
    # ip_interfaces = List[NetworkInterface] = field(default_factory=lambda: [
    #     NetworkInterface('macvtap0', creation_steps=[
    #         # load required kernel module
    #         "lsmod | grep macvlan || modprobe macvlan",
    #         "ip link add link {{ network.ethernet_interface_id }} name {{ network.macvtap_name }} type macvtap mode bridge",
    #         "ip link set {{ network.macvtap_name }} up",
    #     ]),
    # ])

    ethernet_interface_id: str = field(default='enp3s0')
    cidr_range: str = field(default="192.168.1.80/28")

@dataclass
class QemuUser:
    name: str = field(default='root')
    group: str = field(default='root')

@dataclass
class QemuConfig:
    user: QemuUser = field(default_factory=QemuUser)

@dataclass
class AptConfig:
    packages: List[str] = field(default_factory=lambda: [
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
        # "qemu-kvm",
        "libvirt-clients",
        "bridge-utils",
        "libvirt-daemon-system",
        # "qemu-efi",

        # dev packages
        "virt-manager",

        # secureboot packages # TODO
        # "ovmf",
        # "qemu-system-x86",
        # "gpg",
        # "debian-keyring",
    ])
    update: bool = field(default=True)
    upgrade: bool = field(default=True)

@dataclass
class Config:
    hostname: str = field(default='hostname')
    root_user: User = field(default_factory=lambda: User(
        name='root',
        password='root',
    ))
    users: List[User] = field(default_factory=lambda: [User()])
    script: Dict[str, Script] = field(default_factory=lambda: {
        'preseed': Script(location='/root/preseed-setup.sh'),
        'firstboot': Script(location='/root/firstboot-setup.sh'),
    })
    network: NetworkConfig = field(default_factory=NetworkConfig)
    qemu: QemuConfig = field(default_factory=QemuConfig)
    apt: AptConfig = field(default_factory=AptConfig)
    debug: bool = field(default=False)

    def __init__(self, root_auth_keys: list, user_auth_keys: list):
        self.hostname = 'hostname'
        self.root_user = User(
            name='root',
            password='root',
            authorized_keys=root_auth_keys
        )
        self.users = [User(
            name='debian',
            password='debian',
            authorized_keys=user_auth_keys
        )]
        self.script = {
            'preseed': Script(location='/root/preseed-setup.sh'),
            'firstboot': Script(location='/root/firstboot-setup.sh'),
        }
        self.network = NetworkConfig()
        self.qemu = QemuConfig()
        self.apt = AptConfig()
        self.debug = False

    def as_dict(self) -> dict:
        return asdict(self)
