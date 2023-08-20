from contextlib import contextmanager
from dataclasses import dataclass
from os.path import expanduser

from sshconf import read_ssh_config

from dow.svc.data import Machine


@dataclass
class SshConfEntry:
    key: str
    params: dict


@contextmanager
def __conf():
    conf_path = expanduser("~/.ssh/config")
    conf = read_ssh_config(conf_path)
    yield conf
    conf.write(conf_path)


def __map_port(port: int):
    return f"{port} localhost:{port}"


def __create_entry(machine: Machine, root=False) -> SshConfEntry:
    key = f"{machine.name}-dow"
    if root:
        key += "-root"

    params: dict = {
        "HostName": machine.ip,
        "User": machine.username if not root else "root",
        "ForwardAgent": "yes",
    }

    if not root:
        params["LocalForward"] = [__map_port(port) for port in machine.ports]

    return SshConfEntry(key, params)


def update_entry(machine: Machine, root: bool) -> str:
    with __conf() as conf:
        entry = __create_entry(machine, root)

        if entry.key in conf.hosts():
            conf.remove(entry.key)

        conf.add(entry.key, **entry.params)

        return entry.key


def remove_entry(machine: Machine):
    with __conf() as conf:
        for root in [True, False]:
            entry = __create_entry(machine, root)
            key = entry.key
            if key in conf.hosts():
                conf.remove(key)
