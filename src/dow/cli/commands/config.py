from typing import Optional

import click

from dow import config as cfg
from dow import do
from dow.cli.utils import msg, tab_data


@click.group(name="config", help="DOW configuration")
def config():
    pass


@config.command(help="DigitalOcean token")
@click.argument("token", type=str, required=False)
def token(token: Optional[str]):
    if token is None:
        msg(f"Current token: {cfg.do_token()}")
        return

    cfg.set_do_token(token)
    msg(f"Token updated")


@config.command(help="DigitalOcean region")
@click.argument("region", type=str, required=False)
def region(region: Optional[str]):
    if region is None:
        msg(f"Current region: {cfg.do_region()}")
        return

    cfg.set_do_region(region)
    msg(f"Region updated")


@config.group(name="firewalls", help="DigitalOcean firewalls")
def firewalls():
    pass


@firewalls.command(name="list", help="List firewalls")
def list_firewalls():
    firewalls = cfg.do_firewall_ids()
    firewalls_str = "\n".join([f"  {f}" for f in firewalls])
    msg(f"Current firewalls:\n{firewalls_str}")


@firewalls.command(name="add", help="Add firewall")
@click.argument("firewall_id", type=str)
def add_firewall(firewall_id: str):
    cfg.add_firewall_id(firewall_id)
    msg(f"Firewall {firewall_id} added")


@firewalls.command(name="remove", help="Remove firewall")
@click.argument("firewall_id", type=str)
def remove_firewall(firewall_id: str):
    cfg.remove_firewall_id(firewall_id)
    msg(f"Firewall {firewall_id} removed")
