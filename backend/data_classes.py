from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LocatedObject:
    xOffset: float
    yOffset: float
    width: float
    height: float
    className: str


@dataclass_json
@dataclass
class Quantity:
    minQuantity: int
    maxQuantity: int
    className: str


@dataclass_json
@dataclass
class FilterCriteria:
    locatedObjects: List[LocatedObject]
    quantities: List[Quantity]
    classNames: List[str]
    gridWidth: int
    text: Optional[str] = None


@dataclass_json
@dataclass
class Keyframe:
    title: str
    video: str
    vimeoId: str
    idx: int
    totalKfsVid: int
    atTime: str
    description: str
    tags: List[str]


@dataclass_json
@dataclass
class RandomVideo:
    id: str
    vimeoId: str
    atTime: int
