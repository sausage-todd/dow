from typing import Optional

import click
import colorama

from dow import config, do
from dow.cli.utils import msg, tab_data
from dow.config.data import MachineConfig
from dow.svc import create_machine, ssh_config
from dow.svc.data import MachineStatus
from dow.svc.list_machines import full_machine, list_machines
from dow.svc.shutdown import shutdown_machine


@click.group(name="machines", help="Manage machines")
def machines():
    pass


@machines.command(help="List configured machines")
def list():
    def status_mapper(value: MachineStatus):
        if value == MachineStatus.RUNNING:
            return "".join(
                [
                    colorama.Fore.GREEN,
                    colorama.Style.BRIGHT,
                    value.name,
                    colorama.Style.RESET_ALL,
                ]
            )
        elif value == MachineStatus.CONFIG:
            return "".join(
                [
                    colorama.Fore.YELLOW,
                    colorama.Style.BRIGHT,
                    value.name,
                    colorama.Style.RESET_ALL,
                ]
            )
        else:
            return value.name

    tab_data(
        [
            "name",
            "size",
            "image",
            "volume",
            "username",
            "swapsize",
            "status",
            "ip",
            "ports",
        ],
        list_machines(),
        field_mapper={"status": status_mapper},
    )


@machines.command(help="Delete machine")
@click.argument("name", required=True, type=str)
def delete(name: str):
    droplet = do.droplet_find_by_name(name)
    if droplet is not None:
        droplet_id = droplet["id"]
        do.droplet_delete(droplet_id)

        msg(f"Machine '{name}' stopped")

    config.delete_machine(name)
    msg(f"Machine '{name}' deleted")


def __connect_info(machine_config: MachineConfig, droplet: dict):
    machine = full_machine(machine_config, droplet)
    host_key = ssh_config.update_entry(machine)

    msg(f"To connect: ssh {host_key}")


@machines.command(help="Connect to machine")
@click.argument("name", required=True, type=str)
def connect(name: str):
    machine_config = config.get_machine(name)
    droplet = do.droplet_find_by_name(name)
    if droplet is None:
        msg(f"Machine '{name}' not started")
        return

    __connect_info(machine_config, droplet)


@machines.command(help="Start machine")
@click.argument("name", required=True, type=str)
def start(name: str):
    machine_config = config.get_machine(name)
    droplet = do.droplet_find_by_name(name)
    if droplet is not None:
        msg(f"Machine '{name}' already started")
        __connect_info(machine_config, droplet)
        return

    create_machine.create(machine_config)

    droplet = do.droplet_find_by_name(name)
    __connect_info(machine_config, droplet)


@machines.command(help="Stop machine")
@click.argument("name", required=True, type=str)
def stop(name):
    droplet = do.droplet_find_by_name(name)
    if droplet is None:
        msg(f"Machine '{name}' not started")
        return
    shutdown_machine(droplet["id"])

    machine_config = config.get_machine(name)
    machine = full_machine(machine_config, droplet)
    ssh_config.remove_entry(machine)

    msg(f"Machine '{name}' stopped")


@machines.command(help="Create new machine")
@click.option("--name", required=True, type=str, help="Machine name")
@click.option("--size", required=True, type=str, help="Droplet size")
@click.option("--image", required=True, type=str, help="Droplet image")
@click.option("--volume", required=True, type=str, help="Volume name to attach")
@click.option("--username", required=True, type=str, help="Default working username")
@click.option("--swapsize", required=True, type=int, help="Swap size")
def create(name: str, size: str, image: str, volume: str, username: str, swapsize: int):
    machine_config = MachineConfig(
        name=name,
        size=size,
        image=image,
        volume=volume,
        username=username,
        swapsize=swapsize,
    )

    config.add_machine(machine_config)
    msg(f"Created machine {name}")


@machines.command(help="Edit machine")
@click.option("--name", required=True, type=str, help="Machine name")
@click.option("--size", type=str, help="Droplet size")
@click.option("--image", type=str, help="Droplet image")
@click.option("--volume", type=str, help="Volume name to attach")
@click.option("--username", type=str, help="Default working username")
@click.option("--swapsize", type=int, help="Swap size")
def edit(
    name: str,
    size: Optional[str],
    image: Optional[str],
    volume: Optional[str],
    username: Optional[str],
    swapsize: Optional[int],
):
    machine_config = config.get_machine(name)
    new_machine_config = MachineConfig(
        name=name,
        size=size or machine_config.size,
        image=image or machine_config.image,
        volume=volume or machine_config.volume,
        username=username or machine_config.username,
        swapsize=swapsize or machine_config.swapsize,
    )

    config.update_machine(new_machine_config)
    msg(f"Updated machine {name}")


@machines.group(name="ports", help="Manage port forwarding")
def ports():
    pass


@ports.command(help="Add forwarded port")
@click.option("--machine", required=True, type=str, help="Machine name")
@click.option("--port", required=True, type=str, help="Port to forward")
def add(machine: str, port: str):
    machine_config = config.get_machine(machine)
    machine_config.ports.append(port)
    config.update_machine(machine_config)
    msg(f"Added port '{port}' to machine '{machine}'")


@ports.command(help="Remove forwarded port")
@click.option("--machine", required=True, type=str, help="Machine name")
@click.option("--port", required=True, type=str, help="Port to remove")
def remove(machine: str, port: str):
    machine_config = config.get_machine(machine)
    machine_config.ports.remove(port)
    config.update_machine(machine_config)
    msg(f"Removed port '{port}' from machine '{machine}'")
