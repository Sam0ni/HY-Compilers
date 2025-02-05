from dataclasses import dataclass

from objects.types import BasicType


@dataclass
class SymTab():
    variables: dict[str, BasicType]
    parent: "SymTab" | None