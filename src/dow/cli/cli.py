import click

from dow.cli.commands.list_images import list_images
from dow.cli.commands.list_sizes import list_sizes
from dow.cli.commands.machines import machines
from dow.cli.commands.volumes import volumes


@click.group()
def main():
    pass


main.add_command(list_images)
main.add_command(list_sizes)
main.add_command(volumes)
main.add_command(machines)
