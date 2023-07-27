import time

from dow import do
from dow.cli.utils import msg


def __wait_until_shutdown(droplet_id: str, action_id: str):
    for _ in range(6):
        action_status = do.droplet_action_get(droplet_id, action_id)["action"]["status"]
        if action_status == "completed":
            return
        msg(f"Waiting for shutdown to complete ({action_status})")
        time.sleep(5)

    msg("Graceful shutdown failed")


def shutdown_machine(droplet_id: str):
    action_id = do.droplet_shutdown(droplet_id)

    __wait_until_shutdown(droplet_id, action_id)

    do.droplet_delete(droplet_id)
