from dataclasses import dataclass
from typing import Optional


@dataclass
class TravelTime:
    target: str
    bike: str
    public: Optional[str] = None
