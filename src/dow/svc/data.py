from enum import Enum

from pydantic import BaseModel


class MachineStatus(Enum):
    RUNNING = "running"
    CONFIG = "config"


class Machine(BaseModel):
    name: str
    size: str
    volume: str
    image: str
    username: str
    swapsize: int
    status: MachineStatus = MachineStatus.CONFIG
    ip: str = ""
