import click
from requests.api import request

from dow import do
from dow.cli.utils import msg, tab_data


@click.group()
def volumes():
    pass


@volumes.command()
def list():
    tab_data(["name", "size_gigabytes"], do.volumes_list())


@volumes.command()
@click.argument("name")
def delete(name: str):
    do.volume_delete(name)
    msg(f"Deleted volume '{name}'")


@volumes.command()
@click.option("--name", required=True)
@click.option("--size", type=int, required=True)
def create(name: str, size: int):
    do.volume_create(name, size)
    msg(f"Created volume '{name}'")
