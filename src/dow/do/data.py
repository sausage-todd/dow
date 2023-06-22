from dataclasses import dataclass
from os import stat_result

from pydantic import BaseModel


class Distribution(BaseModel):
    slug: str
    name: str
    distribution: str
    description: str
    size_gigabytes: float


class ImageSize(BaseModel):
    slug: str
    memory: int
    vcpus: int
    disk: int
    price_monthly: float
    price_hourly: float
    description: str


class Volume(BaseModel):
    id: str
    name: str
    size_gigabytes: int
