from compiler.objects.token import Token
from compiler.objects.source_location import Source_location
from compiler.parser import Parser
from compiler.assets.test_source import L
import compiler.objects.ast as ast

parse = Parser.parse

def test_parse_binary_op() -> None:
    binary_operation = [Token(loc=Source_location("2 + 5", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + 5", 1, 3), type="operator", text="+"), Token(loc=Source_location("2 + 5", 1, 5), type="int_literal", text="5")]
    assert parse(binary_operation) == [ast.BinaryOp(L,left=ast.Literal(L,2), op="+", right=ast.Literal(L,5))]

def test_parse_binary_error() -> None:
    binary_operation = [Token(loc=Source_location("2 +", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 +", 1, 3), type="int_literal", text="+")]
    try:
        parse(binary_operation)
    except Exception as e:
        assert str(e) == f"{binary_operation[1].loc}: expected an integer literal or and identifier"

def test_parse_binary_identifier() -> None:
    binary_operation = [Token(loc=Source_location("2 + a", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + a", 1, 3), type="int_literal", text="+"), Token(loc=Source_location("2 + a", 1, 5), type="identifier", text="a")]
    assert parse(binary_operation) == [ast.BinaryOp(L,left=ast.Literal(L,2), op="+", right=ast.Identifier(L,"a"))]

def test_parse_three_terms() -> None:
    binary_operation = [Token(loc=Source_location("2 + 5 + a", 1, 1), type="int_literal", text="2"), Token(loc=Source_location("2 + 5 + a", 1, 3), type="operator", text="+"), Token(loc=Source_location("2 + 5 + a", 1, 5), type="int_literal", text="5"), Token(loc=Source_location("2 + 5 + a", 1, 7), type="operator", text="+"), Token(loc=Source_location("2 + 5 + a", 1, 9), type="identifier", text="a")]
    assert parse(binary_operation) == [ast.BinaryOp(L,left=ast.BinaryOp(L,left=ast.Literal(L,2), op="+", right=ast.Literal(L,5)), op="+", right=ast.Identifier(L,"a"))]

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
    assert parse(if_clause) == [ast.IfExpression(L,ast.Identifier(L,"a"), ast.BinaryOp(L,left=ast.Literal(L,5), op="+", right=ast.Literal(L,5)), ast.BinaryOp(L,left=ast.Literal(L,6), op="+", right=ast.Literal(L,6)))]

def test_parse_if_without_else() -> None:
    if_clause = [Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 1), type="identifier", text="if"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 4), type="identifier", text="a"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 6), type="identifier", text="then"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 11), type="int_literal", text="5"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 13), type="operator", text="+"),
                 Token(loc=Source_location("if a then 5 + 5 else 6 + 6", 1, 15), type="int_literal", text="5")]
    assert parse(if_clause) == [ast.IfExpression(L,ast.Identifier(L,"a"), ast.BinaryOp(L,left=ast.Literal(L,5), op="+", right=ast.Literal(L,5)), None)]

def test_parse_if_as_expression() -> None:
    binary_operation = [Token(loc=L, type="int_literal", text="1"),
                        Token(loc=L, type="operator", text="+"),
                        Token(loc=L, type="identifier", text="if"),
                        Token(loc=L, type="identifier", text="true"),
                        Token(loc=L, type="identifier", text="then"),
                        Token(loc=L, type="int_literal", text="2"),
                        Token(loc=L, type="identifier", text="else"),
                        Token(loc=L, type="int_literal", text="3")]
    assert parse(binary_operation) == [ast.BinaryOp(L,ast.Literal(L,1), "+", ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Literal(L,2), ast.Literal(L,3)))]

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
    assert parse(if_clause) == [ast.IfExpression(L,ast.Identifier(L,"a"), ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Literal(L,2), ast.Literal(L,3)), None)]


def test_function_call() -> None:
    function_call = [Token(L, "identifier", "mrFunc"), Token(L, "punctuation", "("), Token(L, "int_literal", "4"), Token(L, "punctuation", ","), Token(L, "identifier", "a"), Token(L, "punctuation", ")")]
    assert parse(function_call) == [ast.Function(L,ast.Identifier(L,"mrFunc"), [ast.Literal(L,4), ast.Identifier(L,"a")])]

def test_parenthesis() -> None:
    parenthesis = [Token(L, "int_literal", "4"), Token(L, "operator", "*"), Token(L, "punctuation", "("), Token(L, "int_literal", "4"), Token(L, "operator", "-"), Token(L, "int_literal", "6"), Token(L, "punctuation", ")")]
    assert parse(parenthesis) == [ast.BinaryOp(L,ast.Literal(L,4), "*", ast.BinaryOp(L,ast.Literal(L,4), "-", ast.Literal(L,6)))]


def test_variable_declaration_error() -> None:
    if_clause = [Token(loc=L, type="identifier", text="if"),
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="identifier", text="then"),Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5")]
    try:
        parse(if_clause)
    except Exception as e:
        assert str(e) == "Source_location(file='testfile', line=10, column=20): variable declaration only allowed in blocks or top-level"

def test_variable_declaration_top() -> None:
    declaration = [Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5")]
    assert parse(declaration) == [ast.Declaration(L,variable=ast.Identifier(L,"x"), value=ast.Literal(L,5), typed=None)]

def test_variable_declaration_block() -> None:
    block = [Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[], ast.Declaration(L,variable=ast.Identifier(L,"x"), value=ast.Literal(L,5), typed=None))]

def test_block_missing_semicolon() -> None:
    block = [Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5"), Token(L, "identifier", "x"), Token(L, "punctuation", "}")]
    try:
        parse(block)
    except Exception as e:
        assert str(e) == "Missing semicolon at Source_location(file='testfile', line=10, column=20)"

def test_block_result() -> None:
    block = [Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5"), Token(L, "punctuation", ";"), Token(L, "identifier", "x"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.Declaration(L,ast.Identifier(L,"x"), ast.Literal(L,5), None)], ast.Identifier(L,"x"))]

def test_block_no_result() -> None:
    block = [Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5"), Token(L, "punctuation", ";"), Token(L, "identifier", "x"), Token(L, "punctuation", ";"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.Declaration(L,ast.Identifier(L,"x"), ast.Literal(L,5), None), ast.Identifier(L,"x")], ast.Literal(None, None))]

def test_block_automatic_semicolons() -> None:
    block = [Token(loc=L, type="punctuation", text="{"), Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "4"), Token(L, "punctuation", "}"), Token(L, "punctuation", "{"), Token(loc=L, type="identifier", text="a"), Token(L, "punctuation", "}"), Token(loc=L, type="punctuation", text="{"), Token(L, "identifier", "var"),Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "int_literal", "5"), Token(L, "punctuation", "}"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.Block(L,[], ast.Declaration(L,ast.Identifier(L,"x"), ast.Literal(L,4), None)), ast.Block(L,[], ast.Identifier(L,"a"))], ast.Block(L,[], ast.Declaration(L,ast.Identifier(L,"x"), ast.Literal(L,5), None)))]

def test_block_automatic_semicolons_1() -> None:
    block = [Token(L, "punctuation", "{"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "punctuation", "{"), Token(L, "identifier", "b"), Token(L, "punctuation", "}"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.Block(L,[], ast.Identifier(L,"a"))], ast.Block(L,[], ast.Identifier(L,"b")))]

def test_block_automatic_semicolons_2() -> None:
    block = [Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "identifier", "b"), Token(L, "punctuation", "}")]
    try:
        parse(block)
    except Exception as e:
        assert str(e) == "Missing semicolon at Source_location(file='testfile', line=10, column=20)"

def test_block_automatic_semicolons_3() -> None:

    block = [Token(L, "punctuation", "{"), Token(L, "identifier", "if"), Token(L, "identifier", "true"), Token(L, "identifier", "then"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "identifier", "b"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Block(L,[], ast.Identifier(L,"a")), None)], ast.Identifier(L,"b"))]

def test_block_automatic_semicolons_4() -> None:

    block = [Token(L, "punctuation", "{"), Token(L, "identifier", "if"), Token(L, "identifier", "true"), Token(L, "identifier", "then"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "punctuation", ";"), Token(L, "identifier", "b"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Block(L,[], ast.Identifier(L,"a")), None)], ast.Identifier(L,"b"))]

def test_block_automatic_semicolons_5() -> None:
    try:
        block = [Token(L, "punctuation", "{"), Token(L, "identifier", "if"), Token(L, "identifier", "true"), Token(L, "identifier", "then"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "identifier", "b"), Token(L, "identifier", "c"), Token(L, "punctuation", "}")]
        parse(block)
    except Exception as e:
        assert str(e) == "Missing semicolon at Source_location(file='testfile', line=10, column=20)"
def test_block_automatic_semicolons_6() -> None:

    block = [Token(L, "punctuation", "{"), Token(L, "identifier", "if"), Token(L, "identifier", "true"), Token(L, "identifier", "then"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "identifier", "b"), Token(L, "punctuation", ";"), Token(L, "identifier", "c"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Block(L,[], ast.Identifier(L,"a")), None), ast.Identifier(L,"b")], ast.Identifier(L,"c"))]

def test_block_automatic_semicolons_7() -> None:

    block = [Token(L, "punctuation", "{"), Token(L, "identifier", "if"), Token(L, "identifier", "true"), Token(L, "identifier", "then"), Token(L, "punctuation", "{"), Token(L, "identifier", "a"), Token(L, "punctuation", "}"), Token(L, "identifier", "else"), Token(L, "punctuation", "{"), Token(L, "identifier", "b"), Token(L, "punctuation", "}"), Token(L, "identifier", "c"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.Block(L,[ast.IfExpression(L,ast.Boolean_literal(L,"true"), ast.Block(L,[], ast.Identifier(L,"a")), ast.Block(L,[], ast.Identifier(L,"b")))], ast.Identifier(L,"c"))]

def test_block_automatic_semicolons_8() -> None:

    block = [Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "punctuation", "{"), Token(L, "punctuation", "{"), Token(L, "identifier", "f"), Token(L, "punctuation", "("), Token(L, "identifier", "a"), Token(L, "punctuation", ")"), Token(L, "punctuation", "}"), Token(L, "punctuation", "{"), Token(L, "identifier", "b"), Token(L, "punctuation", "}"), Token(L, "punctuation", "}")]
    assert parse(block) == [ast.BinaryOp(L,ast.Identifier(L,"x"), "=", ast.Block(L,[ast.Block(L,[], ast.Function(L,ast.Identifier(L,"f"), [ast.Identifier(L,"a")]))], ast.Block(L,[], ast.Identifier(L,"b"))))]

def test_while_loop() -> None:
    loop = [Token(L, "identifier", "while"), Token(L, "identifier", "true"), Token(L, "identifier", "do"), Token(L, "identifier", "a"), Token(L, "operator", "+"), Token(L, "int_literal", "1")]
    assert parse(loop) == [ast.While_loop(L, ast.Boolean_literal(L, "true"), ast.BinaryOp(L, ast.Identifier(L, "a"), "+", ast.Literal(L, 1)))]

def test_typed_variable_dec() -> None:
    declaration = [Token(L, "identifier", "var"), Token(L, "identifier", "a"), Token(L, "punctuation", ":"), Token(L, "identifier", "bool"), Token(L, "operator", "="), Token(L, "identifier", "true")]
    assert parse(declaration) == [ast.Declaration(L, ast.Identifier(L, "a"), ast.Boolean_literal(L, "true"), ast.Identifier(L, "bool"))]

#def test_typed_variable_dec_func() -> None:
    #declaration = [Token(L, "identifier", "var"), Token(L, "identifier", "a"), Token(L, "punctuation", ":"), Token(L, "punctuation", "("), Token(L, "identifier", "bool"), Token(L, "punctuation", ","), Token(L, "identifier", "int"), Token(L, "punctuation", ","), Token(L, "identifier", "str"), Token(L, "punctuation", ")"), Token(L, "operator", "=>"), Token(L, "identifier", "int"), Token(L, "identifier", "true")]

def test_multiple_top_level() -> None:
    code = [Token(L, "identifier", "var"), Token(L, "identifier", "a"), Token(L, "operator", "="), Token(L, "int_literal", "1"), Token(L, "punctuation", ";"), Token(L, "identifier", "print"), Token(L, "punctuation", "("), Token(L, "identifier", "a"), Token(L, "operator", "+"), Token(L, "int_literal", "2"), Token(L, "operator", "=="), Token(L, "int_literal", "3"), Token(L, "punctuation", ")")]
    assert parse(code) == [ast.Declaration(L, ast.Identifier(L, "a"), ast.Literal(L, 1), None), ast.Function(L, ast.Identifier(L, "print"), [ast.BinaryOp(L, ast.BinaryOp(L, ast.Identifier(L, "a"), "+", ast.Literal(L, 2)), "==", ast.Literal(L, 3))])]