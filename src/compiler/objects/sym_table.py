from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from objects.types import BasicType


@dataclass
class SymTab():
    variables: dict[str, BasicType]
    parent: Optional[SymTab] = None