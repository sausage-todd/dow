from contextlib import contextmanager

from dow.cli.utils import DowError
from dow.config.base import read, write
from dow.config.data import MachineConfig


def read_machines() -> list[MachineConfig]:
    return read().machines


@contextmanager
def __update_config():
    config = read()
    yield config
    write(config)


def write_machines(machines: list[MachineConfig]):
    with __update_config() as config:
        config.machines = machines


def __check_empty(value: str, name: str) -> str:
    if not value:
        raise DowError(f"{name} not set")
    return value


def do_token() -> str:
    return __check_empty(read().do_token, "DigitalOcean token")


def do_region() -> str:
    return __check_empty(read().do_region, "DigitalOcean region")


def do_firewall_ids() -> list[str]:
    return read().firewall_ids


def set_do_token(token: str):
    with __update_config() as config:
        config.do_token = token


def set_do_region(region: str):
    with __update_config() as config:
        config.do_region = region


def add_firewall_id(firewall_id: str):
    with __update_config() as config:
        config.firewall_ids.append(firewall_id)


def remove_firewall_id(firewall_id: str):
    with __update_config() as config:
        config.firewall_ids.remove(firewall_id)


def __replace_machine(machines: list[MachineConfig], config: MachineConfig):
    config.ports = list(set(config.ports))

    return [config if m.name == config.name else m for m in machines]


def add_machine(config: MachineConfig):
    machines = read_machines()
    if any(m.name == config.name for m in machines):
        raise DowError(f"Machine '{config.name}' already exists")

    machines = machines + [config]
    write_machines(machines)


def update_machine(config: MachineConfig):
    machines = read_machines()
    if not any(m.name == config.name for m in machines):
        raise DowError(f"Machine '{config.name}' not found")

    machines = __replace_machine(machines, config)
    write_machines(machines)


def get_machine(name: str) -> MachineConfig:
    for machine in read_machines():
        if machine.name == name:
            return machine
    raise DowError(f"Machine {name} not found")


def delete_machine(name: str):
    machines = read_machines()
    if not any(m.name == name for m in machines):
        raise DowError(f"Machine '{name}' not found")
    machines = [m for m in machines if m.name != name]
    write_machines(machines)
