from typing import Optional

import click
import colorama

from dow import config, do
from dow.cli.utils import msg, tab_data
from dow.config.data import MachineConfig
from dow.do import svc
from dow.svc import create_machine
from dow.svc.data import MachineStatus
from dow.svc.list_machines import list_machines


@click.group()
def machines():
    pass


@machines.command()
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
        ],
        list_machines(),
        field_mapper={"status": status_mapper},
    )


@machines.command()
@click.argument("name")
def delete(name: str):
    droplet = do.droplet_find_by_name(name)
    if droplet is not None:
        droplet_id = droplet["id"]
        do.droplet_delete(droplet_id)

        msg(f"Machine '{name}' shutdown")

    config.delete_machine(name)
    msg(f"Machine '{name}' deleted")


@machines.command()
@click.argument("name")
def connect(name: str):
    machine_config = config.get_machine(name)
    droplet = do.droplet_find_by_name(name)
    if droplet is None:
        msg(f"Machine '{name}' not started")
        return

    ip_addr = svc.droplet_network(droplet)

    msg(f"To connect: ssh -A {machine_config.username}@{ip_addr}")


@machines.command()
@click.argument("name")
def start(name: str):
    droplet = do.droplet_find_by_name(name)
    if droplet is not None:
        msg(f"Machine '{name}' already started")
        return

    machine_config = config.get_machine(name)
    create_machine.create(machine_config)


@machines.command()
@click.argument("name")
def shutdown(name):
    droplet = do.droplet_find_by_name(name)
    if droplet is None:
        msg(f"Machine '{name}' not started")
        return
    droplet_id = droplet["id"]
    do.droplet_delete(droplet_id)

    msg(f"Machine '{name}' shutdown")


@machines.command()
@click.option("--name", required=True)
@click.option("--size", required=True)
@click.option("--image", required=True)
@click.option("--volume", required=True)
@click.option("--username", required=True)
@click.option("--swapsize", required=True, type=int)
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


@machines.command()
@click.option("--name", required=True)
@click.option("--size")
@click.option("--image")
@click.option("--volume")
@click.option("--username")
@click.option("--swapsize", type=int)
def update(
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

    config.add_machine(new_machine_config)
    msg(f"Updated machine {name}")