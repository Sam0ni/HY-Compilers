from dataclasses import dataclass


@dataclass(frozen=True)
class Type():
    """Base Class"""

@dataclass(frozen=True)
class BasicType(Type):
    name: str

    def __eq__(self, other):
        if self.name == other.name:
            return True

Int = BasicType("Int")
Bool = BasicType("Bool")
Unit = BasicType("Unit")

@dataclass(frozen=True)
class FunType(Type):
    parameter_types: list[BasicType]
    result_type: BasicType

    def __eq__(self, other):
        if self.parameter_types == other.parameter_types and self.result_type == other.result_type:
            return True