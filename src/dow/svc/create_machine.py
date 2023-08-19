import os
import textwrap
import time
from contextlib import contextmanager

from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import NoValidConnectionsError

from dow import config, do
from dow.cli.utils import msg
from dow.config.data import MachineConfig
from dow.do import svc


def __create_user_data(
    install_log: str, username: str, volume_name: str, swapsize: int
):
    with open(os.environ["USER_DATA_FILE"], "r") as f:
        user_data = f.read()
        return (
            textwrap.dedent(
                f"""\
                #!/bin/bash

                readonly INSTALL_LOG="{install_log}"
                readonly USERNAME="{username}"
                readonly VOLUME_NAME="{volume_name}"
                readonly SWAPSIZE="{swapsize}"

                """
            )
            + user_data
        )


def __wait_until_active(droplet_id: str):
    while True:
        status = svc.droplet_status(droplet_id)
        if status == "active":
            msg("Status 'active', continuing")
            return

        msg(f"Status '{status}', waiting...")
        time.sleep(5)


@contextmanager
def __with_ssh(ip_addr: str):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy)
    client.connect(ip_addr, username="root", timeout=5)
    try:
        yield client
    finally:
        client.close()


def __wait_until_connectable(ip_addr: str):
    msg(f"Waiting for SSH to become available at {ip_addr}")
    while True:
        try:
            with __with_ssh(ip_addr) as _:
                return
        except (TimeoutError, NoValidConnectionsError):
            msg("Still waiting...")
            time.sleep(5)


def __wait_until_log_is_ready(ip_addr: str, install_log: str):
    msg("Waiting for install log to be ready")
    with __with_ssh(ip_addr) as client:
        while True:
            _, stdout, _ = client.exec_command(
                f"test -f {install_log} && echo 'y' || echo 'n'"
            )
            result = stdout.read().decode("utf-8").strip()
            if result == "y":
                return

            msg("Still waiting...")
            time.sleep(5)


def __wait_until_inited(ip_addr: str, install_log: str):
    msg("Waiting for machine init to complete")
    with __with_ssh(ip_addr) as client:
        _, stdout, _ = client.exec_command(f"tail -f {install_log}")

        def line_buffered(f):
            line_buf = ""
            while not f.channel.exit_status_ready():
                line_buf += f.read(1).decode("utf-8")
                if line_buf.endswith("\n"):
                    yield line_buf.strip()
                    line_buf = ""

        for line in line_buffered(stdout):
            if line == "done":
                break
            msg(line)


def create(machine_config: MachineConfig, with_user_data: bool):
    volume_id = do.volume_find_by_name(machine_config.volume)["id"]
    msg(f"Using volume '{machine_config.volume}' ({volume_id})")

    install_log = "/tmp/install.log"

    user_data = __create_user_data(
        install_log=install_log,
        username=machine_config.username,
        volume_name=machine_config.volume,
        swapsize=machine_config.swapsize,
    )

    ssh_keys = do.ssh_keys()["ssh_keys"]
    ssh_key_names = [k["name"] for k in ssh_keys]
    ssh_key_ids = [k["id"] for k in ssh_keys]
    msg(f"Using SSH keys: {ssh_key_names}")

    droplet_id = do.droplet_create(
        name=machine_config.name,
        size=machine_config.size,
        image=machine_config.image,
        ssh_keys=ssh_key_ids,
        user_data=user_data if with_user_data else "",
        volumes=[volume_id],
    )

    msg(f"Created droplet {droplet_id}")

    for firewall_id in config.do_firewall_ids():
        do.firewall_add_droplet(
            firewall_id,
            droplet_id,
        )

    __wait_until_active(droplet_id)

    ip_addr = svc.droplet_network(droplet_id)
    msg(f"Got IP address: {ip_addr}")

    __wait_until_connectable(ip_addr)

    if with_user_data:
        __wait_until_log_is_ready(ip_addr, install_log)
        __wait_until_inited(ip_addr, install_log)

    msg(f"Machine '{machine_config.name}' is ready")
