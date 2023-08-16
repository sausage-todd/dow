from pydantic import BaseModel


class MachineConfig(BaseModel):
    name: str
    size: str
    volume: str
    image: str
    swapsize: int
    username: str
    ports: list[str]
    init: str = ""
