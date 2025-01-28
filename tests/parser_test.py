from compiler.objects.token import Token
from compiler.objects.source_location import Source_location
from compiler.parser import Parser
from compiler.assets.test_source import L
import compiler.objects.ast as ast

parse = Parser.parse

def test_parse_binary_op() -> None:
    binary_operation = [Token(loc=Source_location("2 + 5", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + 5", 1, 3), type="operator", text="+"), Token(loc=Source_location("2 + 5", 1, 5), type="int_literal", text="5")]
    assert parse(binary_operation) == ast.BinaryOp(left=ast.Literal(2), op="+", right=ast.Literal(5))

def test_parse_binary_error() -> None:
    binary_operation = [Token(loc=Source_location("2 +", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 +", 1, 3), type="int_literal", text="+")]
    try:
        parse(binary_operation)
    except Exception as e:
        assert str(e) == f"{binary_operation[1].loc}: expected an integer literal or and identifier"

def test_parse_binary_identifier() -> None:
    binary_operation = [Token(loc=Source_location("2 + a", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + a", 1, 3), type="int_literal", text="+"), Token(loc=Source_location("2 + a", 1, 5), type="identifier", text="a")]
    assert parse(binary_operation) == ast.BinaryOp(left=ast.Literal(2), op="+", right=ast.Identifier("a"))

def test_parse_three_terms() -> None:
    binary_operation = [Token(loc=Source_location("2 + 5 + a", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + 5 + a", 1, 3), type="operator", text="+"), Token(loc=Source_location("2 + 5 + a", 1, 5), type="int_literal", text="5"), Token(loc=Source_location("2 + 5 + a", 1, 7), type="operator", text="+"), Token(loc=Source_location("2 + 5 + a", 1, 9), type="identifier", text="a")]
    assert parse(binary_operation) == ast.BinaryOp(left=ast.BinaryOp(left=ast.Literal(2), op="+", right=ast.Literal(5)), op="+", right=ast.Identifier("a"))

def test_parse_bad_end_error() -> None:
    binary_operation = [Token(loc=Source_location("2 + 5 a", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + 5 a", 1, 3), type="operator", text="+"), Token(loc=Source_location("2 + 5 a", 1, 5), type="int_literal", text="5"), Token(loc=Source_location("2 + 5 a", 1, 7), type="identifier", text="a")]
    try:
        parse(binary_operation)
    except Exception as e:
        assert str(e) == f"Source_location(file='2 + 5 a', line=1, column=7): unexpected term: a"

def test_parse_empty_error() -> None:
    binary_operation = []
    try:
        parse(binary_operation)
    except Exception as e:
        assert str(e) == f"The input is empty"

def test_parse_if_else_clause() -> None:
    if_clause = [Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 1), type="identifier", text="if"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 4), type="identifier", text="a"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 6), type="identifier", text="then"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 11), type="int_literal", text="5"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 13), type="operator", text="+"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 15), type="int_literal", text="5"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 17), type="identifier", text="else"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 22), type="int_literal", text="6"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 24), type="operator", text="+"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 26), type="int_literal", text="6")]
    assert parse(if_clause) == ast.IfExpression(ast.Identifier("a"), ast.BinaryOp(left=ast.Literal(5), op="+", right=ast.Literal(5)), ast.BinaryOp(left=ast.Literal(6), op="+", right=ast.Literal(6)))

def test_parse_if_without_else() -> None:
    if_clause = [Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 1), type="identifier", text="if"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 4), type="identifier", text="a"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 6), type="identifier", text="then"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 11), type="int_literal", text="5"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 13), type="operator", text="+"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 15), type="int_literal", text="5")]
    assert parse(if_clause) == ast.IfExpression(ast.Identifier("a"), ast.BinaryOp(left=ast.Literal(5), op="+", right=ast.Literal(5)), None)

def test_parse_if_as_expression() -> None:
    binary_operation = [Token(loc=L, type="int_literal", text="1"),
                        Token(loc=L, type="operator", text="+"),
                        Token(loc=L, type="identifier", text="if"),
                        Token(loc=L, type="identifier", text="true"),
                        Token(loc=L, type="identifier", text="then"),
                        Token(loc=L, type="int_literal", text="2"),
                        Token(loc=L, type="identifier", text="else"),
                        Token(loc=L, type="int_literal", text="3")]
    assert parse(binary_operation) == ast.BinaryOp(ast.Literal(1), "+", ast.IfExpression(ast.Identifier("true"), ast.Literal(2), ast.Literal(3)))

def test_nested_if() -> None:
    if_clause = [
        Token(loc=L, type="identifier", text="if"),
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="identifier", text="then"),
        Token(loc=L, type="identifier", text="if"),
        Token(loc=L, type="identifier", text="true"),
        Token(loc=L, type="identifier", text="then"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="identifier", text="else"),
        Token(loc=L, type="int_literal", text="3")
    ]
    assert parse(if_clause) == ast.IfExpression(ast.Identifier("a"), ast.IfExpression(ast.Identifier("true"), ast.Literal(2), ast.Literal(3)), None)


def test_function_call() -> None:
    function_call = [Token(L, "identifier", "mrFunc"), Token(L, "punctuation", "("), Token(L, "int_literal", "4"), Token(L, "punctuation", ","), Token(L, "identifier", "a"), Token(L, "punctuation", ")")]
    assert parse(function_call) == ast.Function(ast.Identifier("mrFunc"), [ast.Literal(4), ast.Identifier("a")])

def test_parenthesis() -> None:
    parenthesis = [Token(L, "int_literal", "4"), Token(L, "operator", "*"), Token(L, "punctuation", "("), Token(L, "int_literal", "4"), Token(L, "operator", "-"), Token(L, "int_literal", "6"), Token(L, "punctuation", ")")]
    assert parse(parenthesis) == ast.BinaryOp(ast.Literal(4), "*", ast.BinaryOp(ast.Literal(4), "-", ast.Literal(6)))