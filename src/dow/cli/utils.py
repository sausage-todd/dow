from typing import Callable, Optional

import click
import colorama
from tabulate import tabulate


def tab_data(
    fields: list[str],
    items: list,
    field_mapper: Optional[dict[str, Callable]] = None,
):
    if field_mapper is None:
        field_mapper = {}
    data = [fields]
    for item in items:
        row = []
        for f in fields:
            value = getattr(item, f)
            if f in field_mapper:
                row.append(field_mapper[f](value))
            else:
                row.append(str(value))
        data.append(row)
    click.echo(tabulate(data, tablefmt="plain"))


def msg(msg: str):
    click.echo(
        "".join(
            [
                colorama.Fore.YELLOW,
                colorama.Style.BRIGHT,
                "[+] ",
                colorama.Style.RESET_ALL,
                msg,
            ]
        ),
        err=True,
    )
