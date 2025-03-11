from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from compiler.typechecker import typechecker
from compiler.objects.node_types import Int, Bool, Unit, Type, FunType
from compiler.objects.sym_table import SymTab



def test_typechecker_binaryop() -> None:
    tokens = Tokenizer.tokenize("1 + 2")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Int

def test_typechecker_binaryop2() -> None:
    tokens = Tokenizer.tokenize("1 < 2")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Bool

def test_typechecker_binaryop3() -> None:
    tokens = Tokenizer.tokenize("1 == 2")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Bool

def test_typechecker_if_then_else() -> None:
    tokens = Tokenizer.tokenize("if true then 1 else 2")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Int

def test_typechecker_if_then() -> None:
    tokens = Tokenizer.tokenize("if true then 1")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Unit

def test_typechecker_literal() -> None:
    tokens = Tokenizer.tokenize("1")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Int

def test_typechecker_identifier() -> None:
    tokens = Tokenizer.tokenize("a")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed, SymTab({"a": Bool}, None)) == Bool

def test_typechecker_declaration() -> None:
    tokens = Tokenizer.tokenize("var a = 1")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Unit

def test_typechecker_unary() -> None:
    tokens = Tokenizer.tokenize("--1")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Int

def test_typechecker_bool_literal() -> None:
    tokens = Tokenizer.tokenize("false")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Bool

def test_typechecker_block() -> None:
    tokens = Tokenizer.tokenize("{var a = 10; a}")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Int

def test_typechecker_block2() -> None:
    tokens = Tokenizer.tokenize("{var a = 10; a;}")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Unit

def test_typechecker_block3() -> None:
    tokens = Tokenizer.tokenize("{}")
    parsed = Parser.parse(tokens)
    print(typechecker(parsed))
    assert typechecker(parsed) == Unit

def test_typechecker_while() -> None:
    tokens = Tokenizer.tokenize("while true do 1")
    parsed = Parser.parse(tokens)
    assert typechecker(parsed) == Unit