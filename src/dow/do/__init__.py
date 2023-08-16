import os

from dow.do.base import delete, get, post
from dow.do.data import Distribution, ImageSize, Volume


def ssh_keys():
    return get("/account/keys")


def add_droplets_to_firewall():
    pass


def list_images():
    res = get("/images", params={"type": "distribution"}, per_page=200)
    return [Distribution(**i) for i in res["images"]]


def list_sizes() -> list[ImageSize]:
    result = []

    page = 1
    while True:
        res = get("/sizes", page=page, per_page=200)

        result += [ImageSize(**s) for s in res["sizes"]]

        if "pages" not in res["links"] or "next" not in res["links"]["pages"]:
            break
        page += 1

    return result


def volumes_list() -> list[Volume]:
    return [
        Volume(**v, fs_type=v["filesystem_type"]) for v in get("/volumes")["volumes"]
    ]


def volume_create(
    name: str,
    size_gigabytes: int,
    fs_type: str,
):
    return post(
        "/volumes",
        name=name,
        region=os.environ["DO_REGION"],
        size_gigabytes=size_gigabytes,
        filesystem_type=fs_type,
    )


def volume_resize(name: str, size_gigabytes: int):
    volume = volume_find_by_name(name)
    volume_id = volume["id"]

    body = {
        "type": "resize",
        "size_gigabytes": size_gigabytes,
        "region": os.environ["DO_REGION"],
    }

    return post(f"/volumes/{volume_id}/actions", **body)


def volume_find_by_name(name: str):
    result = get("/volumes", name=name)
    if len(result["volumes"]) == 0:
        raise Exception(f"Volume {name} not found")
    return result["volumes"][0]


def volume_delete(name: str):
    volume = volume_find_by_name(name)

    volume_id = volume["id"]

    delete(f"/volumes/{volume_id}")


def droplet_find_by_id(droplet_id: str | int):
    result = get(f"/droplets/{droplet_id}")
    return result["droplet"]


def droplet_create(
    name: str,
    size: str,
    image: str,
    ssh_keys: list[str],
    user_data: str,
    volumes: list[str],
) -> str:
    result = post(
        "/droplets",
        name=name,
        region=os.environ["DO_REGION"],
        size=size,
        image=image,
        ssh_keys=ssh_keys,
        user_data=user_data,
        volumes=volumes,
    )
    return result["droplet"]["id"]


def firewall_add_droplet(firewall_id: str, droplet_id: str):
    return post(f"/firewalls/{firewall_id}/droplets", droplet_ids=[droplet_id])


def droplets_list():
    return get("/droplets")["droplets"]


def droplet_find_by_name(name: str):
    result = get("/droplets", name=name)
    if len(result["droplets"]) == 0:
        return None

    return result["droplets"][0]


def droplet_delete(droplet_id: str):
    delete(f"/droplets/{droplet_id}")


def droplet_shutdown(droplet_id: str):
    body = {
        "type": "shutdown",
    }
    result = post(f"/droplets/{droplet_id}/actions", **body)
    return result["action"]["id"]


def droplet_action_get(droplet_id: str, action_id: str):
    return get(f"/droplets/{droplet_id}/actions/{action_id}")
