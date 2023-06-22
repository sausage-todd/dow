from pydantic import BaseModel


class MachineConfig(BaseModel):
    name: str
    size: str
    volume: str
    image: str
    swapsize: int
    username: str
    init: str = ""
