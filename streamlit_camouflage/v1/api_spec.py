from typing import List
from pydantic import BaseModel


class Color(BaseModel):
    r: float
    g: float
    b: float
    hex: str
    pct: float
    name: str

class Colors(BaseModel):
    colors: List[Color]

class Outfit(BaseModel):
    outfit: List[Colors]

class Matches(BaseModel):
    matches: List[str]