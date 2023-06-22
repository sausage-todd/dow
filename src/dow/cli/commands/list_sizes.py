import click
from tabulate import tabulate

from dow import do
from dow.cli.utils import tab_data


@click.command(name="list-sizes")
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
