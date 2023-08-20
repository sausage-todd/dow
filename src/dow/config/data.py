from pydantic import BaseModel


class MachineConfig(BaseModel):
    name: str
    size: str
    volume: str
    image: str
    swapsize: int
    username: str
    ports: list[int]
    init: str = ""


class Config(BaseModel):
    do_token: str
    do_region: str
    firewall_ids: list[str]
    machines: list[MachineConfig]

    @staticmethod
    def empty() -> "Config":
        return Config(
            do_token="",
            do_region="",
            firewall_ids=[],
            machines=[],
        )

    def validate(self):
        if not self.do_token:
            raise Exception("DigitalOcean token not set")
        if not self.do_region:
            raise Exception("DigitalOcean region not set")
