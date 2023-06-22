from dow.config.base import read, write
from dow.config.data import MachineConfig


def read_machines() -> list[MachineConfig]:
    result = []

    for name, params in read().items():
        result.append(MachineConfig(name=name, **params))

    return result


def add_machine(config: MachineConfig):
    data = read()
    machine_dict = config.dict()
    del machine_dict["name"]
    data[config.name] = machine_dict
    write(data)


def get_machine(name: str) -> MachineConfig:
    for machine in read_machines():
        if machine.name == name:
            return machine
    raise Exception(f"Machine {name} not found")


def delete_machine(name: str):
    data = read()
    if name not in data:
        raise Exception(f"Machine '{name}' not found")
    del data[name]
    write(data)
