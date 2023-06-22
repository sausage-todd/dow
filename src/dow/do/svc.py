from dow.do import droplet_find_by_id


def __get_droplet(droplet: dict | str | int):
    if type(droplet) == str or type(droplet) == int:
        return droplet_find_by_id(droplet)
    elif type(droplet) == dict:
        return droplet
    else:
        raise Exception(f"Unknown param type {type(droplet)}")


def droplet_network(droplet: dict | str | int):
    droplet = __get_droplet(droplet)

    v4_networks = droplet["networks"]["v4"]
    public_networks = [n for n in v4_networks if n["type"] == "public"]
    return public_networks[0]["ip_address"]


def droplet_status(droplet: dict | str | int):
    droplet = __get_droplet(droplet)

    return droplet["status"]
