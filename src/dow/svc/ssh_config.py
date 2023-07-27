from contextlib import contextmanager
from os.path import expanduser

from sshconf import read_ssh_config

from dow.svc.data import Machine


@contextmanager
def __conf():
    conf_path = expanduser("~/.ssh/config")
    conf = read_ssh_config(conf_path)
    yield conf
    conf.write(conf_path)


def __map_port(port: str):
    return f"{port} localhost:{port}"


def update_entry(machine: Machine):
    with __conf() as conf:
        key = f"{machine.name}-dow"
        if key in conf.hosts():
            conf.remove(key)

        conf.add(
            key,
            HostName=machine.ip,
            User=machine.username,
            ForwardAgent="yes",
            LocalForward=[__map_port(port) for port in machine.ports],
        )

        return key


def remove_entry(machine: Machine):
    with __conf() as conf:
        key = f"{machine.name}-dow"
        if key in conf.hosts():
            conf.remove(key)
