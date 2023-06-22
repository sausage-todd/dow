from dow import config, do
from dow.do import svc
from dow.svc import data


def __find_droplet_by_name(droplets: list, name: str):
    for droplet in droplets:
        if droplet["name"] == name:
            return droplet
    return None


def list_machines():
    result = []
    droplets = do.droplets_list()

    machine_configs = config.read_machines()

    for machine_config in machine_configs:
        droplet = __find_droplet_by_name(droplets, machine_config.name)
        if droplet is None:
            result.append(data.Machine(**machine_config.dict()))
            continue

        result.append(
            data.Machine(
                **machine_config.dict(),
                status=data.MachineStatus.RUNNING,
                ip=svc.droplet_network(droplet),
            )
        )

    return result
