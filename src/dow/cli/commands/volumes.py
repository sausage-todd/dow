import click

from dow import do
from dow.cli.utils import msg, tab_data


@click.group(name="volumes", help="Manage volumes")
def volumes():
    pass


@volumes.command(help="List volumes")
def list():
    tab_data(["name", "size_gigabytes", "fs_type"], do.volumes_list())


@volumes.command(help="Delete volume")
@click.argument("name")
def delete(name: str):
    do.volume_delete(name)
    msg(f"Deleted volume '{name}'")


@volumes.command(help="Create volume")
@click.option("--name", required=True, type=str, help="Volume name")
@click.option("--size", required=True, type=int, help="Volume size in GB")
@click.option(
    "--fs-type",
    required=False,
    type=click.Choice(["ext4", "xfs"]),
    help="Filesystem type",
)
def create(name: str, size: int, fs_type: str):
    do.volume_create(name, size, fs_type)
    msg(f"Created volume '{name}'")


@volumes.command(help="Resize volume")
@click.option("--name", required=True, type=str, help="Volume name")
@click.option("--size", required=True, type=int, help="Volume size in GB")
def resize(name: str, size: int):
    do.volume_resize(name, size)
    msg(f"Resized volume '{name}' to {size}GB")
