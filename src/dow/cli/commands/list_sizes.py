import click

from dow import do
from dow.cli.utils import tab_data


@click.command(name="list-sizes", help="List available droplet sizes")
def list_sizes():
    fields = [
        "slug",
        "memory",
        "vcpus",
        "disk",
        "price_monthly",
        "price_hourly",
        "description",
    ]
    tab_data(fields, do.list_sizes())
