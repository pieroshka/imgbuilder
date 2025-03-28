import subprocess
import logging
import typing
import uuid
import os
import shutil
import tempfile
import pathlib
from jinja2 import Environment, FileSystemLoader
from functools import cached_property
from utils.vm import VM
from utils.config import get_config


class MultipassException(Exception):
    ...


class Multipass(VM):
    _workdir = "/home/ubuntu/workspace"
    _templates_paths = [
        "templates/firstboot",
        "templates/preseed",
        "templates",
    ]

    def __init__(
        self,
        flash_target_config_name: str,
        auth: str,
        cpus: int = 4,
        memory: str = "8G",
        disk: str = "7G",
        auth_keys: list = [],
    ):
        self._authenticate(auth)

        self.config = get_config(flash_target_config_name, auth_keys, auth_keys)
        self._machine_name = f"geniso-{uuid.uuid4()}"
        self._provision_vm(cpus, memory, disk)
        self.cmd(f"mkdir -p {self._workdir}", become=False, cwd=None)

    def __enter__(self):
        logging.debug(f"Creating temporary directory {self._tempdir}")
        _ = self._tempdir
        return self

    def __exit__(self, reason: typing.Optional[Exception], traceback, *args):
        if os.path.isdir(self._tempdir):
            logging.debug(f"Removing temporary directory {self._tempdir}")
            shutil.rmtree(self._tempdir)

        self._destroy_vm()

    def _provision_vm(
        self, cpus: int, memory: str, disk: str
    ) -> None:
        _machine_stats = {"cpus": cpus, "memory": memory, "disk": disk}
        logging.debug(f"Provisioning VM {self._machine_name}: {_machine_stats}")

        self._shell_cmd(
            f"multipass launch --name {self._machine_name} --cpus {cpus} --memory {memory} --disk {disk}"
        )

    def _destroy_vm(self) -> None:
        logging.debug(f"Destroying VM {self._machine_name}")
        self._shell_cmd(f"multipass stop {self._machine_name}")
        self._shell_cmd(f"multipass delete {self._machine_name}")

    def _authenticate(self, auth: str):
        logging.info(
            "Authenticating multipass. You may need to input the sudo password now"
        )
        self._shell_cmd(
            f"sudo multipass authenticate {auth}",
        )

    def _build_forwarded_cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
    ) -> str:
        _cmd = command
        if "|" in _cmd:
            # handle commands with pipe
            _cmd = f"'{_cmd}'"

        if become:
            _cmd = f"sudo {_cmd}"

        _workdir = ""
        if cwd is not None:
            if not cwd.startswith("/"):
                cwd = f"{self._workdir}/{cwd}"

            _workdir = f"--working-directory {cwd}"

        return f"multipass exec {_workdir} {self._machine_name} -- {_cmd}"

    # invoke a command on the local machine
    def _shell_cmd(self, cmd: str, stdin: str | bytes = "", pipe: bool = True) -> str:
        popen_kwargs = {"shell": True, "text": isinstance(stdin, str)}

        if pipe:
            popen_kwargs.update(
                {
                    "stdin": subprocess.PIPE,
                    "stdout": subprocess.PIPE,
                    "stderr": subprocess.PIPE,
                }
            )

        proc = subprocess.Popen(cmd, **popen_kwargs)

        if pipe:
            stdout, stderr = proc.communicate(stdin)
            if proc.returncode != 0:
                raise MultipassException(stderr)

            return stdout.strip()
        else:
            proc.communicate()

    # invoke a command inside the multipass VM
    def _forward_cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str | bytes = "",
        pipe: bool = True,
    ) -> str:
        logging.debug(f"Running command: {command}")
        return self._shell_cmd(self._build_forwarded_cmd(command, become, cwd), stdin, pipe)

    def _transfer(self, src: str, dest: str) -> str:
        with open(src, 'rb') as fptr:
            return self._shell_cmd(f'multipass transfer - {dest}', stdin=fptr.read())

    @cached_property
    def _jinja_env(self) -> Environment:
        jinja_loader = FileSystemLoader(Multipass._templates_paths)
        return Environment(loader=jinja_loader)

    @cached_property
    def _tempdir(self) -> str:
        tempdir = tempfile.mkdtemp()
        return tempdir

    def upload(self, src: str, dest: str = ".", destdir: bool = True) -> str:
        parsed_path = pathlib.Path(dest)
        if not parsed_path.is_absolute():
            parsed_path = pathlib.Path(self._workdir).joinpath(parsed_path)
        
        if destdir:
            parsed_path = parsed_path.joinpath(pathlib.Path(src).name)

        logging.debug(f"Uploading file {os.path.basename(src)}")
        return self._transfer(src, f"{self._machine_name}:{parsed_path.as_posix()}")

    def download(self, src: str, dest: str = ".") -> str:
        if not src.startswith("/"):
            src = f"{self._workdir}/{src}"

        _dest = os.path.abspath(dest)
        logging.debug(f"Ensuring {_dest} exists")
        os.makedirs(os.path.abspath(dest), exist_ok=True)

        logging.debug(f"Downloading file {os.path.basename(src)}")
        return self._shell_cmd(f"sudo multipass transfer {self._machine_name}:{src} {_dest}")

    def upload_rendered_template(
        self, template_name: str, dest_fname: str = None
    ) -> str:
        if dest_fname is None:
            dest_fname = template_name.removesuffix(".j2").removesuffix(".jinja2")

        preseed_rendered_fname = os.path.join(self._tempdir, dest_fname)
        with open(preseed_rendered_fname, "w") as fptr:
            _template = self._jinja_env.get_template(template_name)
            _rendered_template = _template.render(self.config.as_dict())
            fptr.write(_rendered_template)

        return self.upload(preseed_rendered_fname)

    def cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str = "",
        pipe: bool = True,
    ) -> str:
        return self._forward_cmd(command, become, cwd, stdin, pipe)
