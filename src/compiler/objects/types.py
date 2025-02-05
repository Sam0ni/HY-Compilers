from dataclasses import dataclass


@dataclass
class Type():
    """Base Class"""

@dataclass
class BasicType(Type):
    name: str

Int = BasicType("Int")
Bool = BasicType("Bool")
Unit = BasicType("Unit")

@dataclass
class FunType(Type):
    parameter_types: list[BasicType]
    result_type: BasicType