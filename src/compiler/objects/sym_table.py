from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from objects.node_types import BasicType
from objects.ir_variables import IRVar


@dataclass
class SymTab():
    variables: dict[str, BasicType | IRVar]
    parent: Optional[SymTab] = None

    def require(self, vari: str):
        cur = self
        while True:
            if vari in cur.variables.keys():
                return cur.variables[vari]
            if cur.parent:
                cur = cur.parent
                continue
            else:
                return None
            
    def add_local(self, vari: str, val: BasicType | IRVar):
        self.variables[vari] = val