import click
import colorama
import requests as r

from dow import config

BASE_URL = "https://api.digitalocean.com/v2"


def __req(
    method: str,
    url_path: str,
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    params: dict = None,
):
    if headers is None:
        headers = {}

    token = config.do_token()
    headers["Authorization"] = f"Bearer {token}"

    url = f"{BASE_URL}{url_path}"
    click.echo(
        "".join(
            [
                colorama.Fore.LIGHTBLACK_EX,
                colorama.Style.BRIGHT,
                method,
                " ",
                url,
                (" " + str(params)) if params is not None else "",
                colorama.Style.RESET_ALL,
            ]
        ),
        err=True,
    )
    res = r.request(method, url, data=data, headers=headers, params=params, json=json)
    if not res.ok:
        raise Exception(f"Error: {res.status_code} {res.reason} {res.text}")

    if len(res.text) == 0:
        return {}

    return res.json()


def get(url_path, **params):
    return __req("GET", url_path, params=params)


def post(url_path, **json):
    return __req("POST", url_path, json=json)


def delete(url_path, **params):
    return __req("DELETE", url_path, params=params)
