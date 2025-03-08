from dataclasses import dataclass, field
from typing import Literal as Lit
from objects.node_types import BasicType, Type, Unit

from objects.source_location import Source_location


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    loc: Source_location | None

    type: Type = field(kw_only = True, default=Unit)

    def __eq__(self, other):
        if self.loc == other.loc:
            return True

@dataclass
class Literal(Expression):
    value: int | bool

    def __eq__(self, other):
        if self.value == other.value:
            return True

@dataclass
class Identifier(Expression):
    name: str

    def __eq__(self, other):
        if self.name == other.name:
            return True
        
@dataclass
class Boolean_literal(Expression):
    boolean: Lit["true", "false"]

    def __eq__(self, other):
        if self.boolean == other.boolean:
            return True

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

    def __eq__(self, other):
        if self.left == other.left and self.op == other.op and self.right == other.right:
            return True
        
@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

    def __eq__(self, other):
        if self.cond == other.cond and self.then_clause == other.then_clause and self.else_clause == other.else_clause:
            return True
        
@dataclass
class Function(Expression):
    name: Identifier
    arguments: list[Expression]

    def __eq__(self, other):
        if self.name == other.name and self.arguments == other.arguments:
            return True
        
@dataclass
class Unary(Expression):
    operators: list[str]
    exp: Expression

    def __eq__(self, other):
        if self.operators == other.operators and self.exp == other.exp:
            return True

@dataclass
class Block(Expression):
    sequence: list[Expression]
    result: Expression | None

    def __eq__(self, other):
        if self.sequence == other.sequence and self.result == other.result:
            return True
        
@dataclass
class FunctionTypeExpression(Expression):
    variable_types: list[Expression]
    result_type: Expression

    def __eq__(self, other):
        if self.variable_types == other.variable_types and self.result_type == other.result_type:
            return True
        
@dataclass
class Declaration(Expression):
    variable: Identifier
    value: Expression
    typed: FunctionTypeExpression | BasicType | None

    def __eq__(self, other):
        if self.variable == other.variable and self.value == other.value:
            return True
    
@dataclass
class While_loop(Expression):
    condition: Expression
    itering: Expression

    def __eq__(self, other):
        if self.condition == other.condition and self.itering == other.itering:
            return True