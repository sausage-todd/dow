import click

from dow import do
from dow.cli.utils import tab_data


@click.command(name="list-images")
def list_images():
    fields = [
        "slug",
        "name",
        "distribution",
        "description",
        "size_gigabytes",
    ]
    tab_data(fields, do.list_images())
