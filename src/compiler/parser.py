from compiler.objects.token import Token
import compiler.objects.ast as ast
from compiler.assets.test_source import L
from compiler.objects.node_types import Bool, Unit, Int

class Parser:
    @staticmethod
    def parse(tokens: list[Token]) -> ast.Expression:
        pos = 0

        left_associative_binary_operators = [
            ['or'],
            ['and'],
            ['==', '!='],
            ['<', '<=', '>', '>='],
            ['+', '-'],
            ['*', '/', "%"],
        ]

        def peek() -> Token:
            try:
                if pos < len(tokens):
                    return tokens[pos]
                else:
                    return Token(loc=tokens[-1].loc, type="end", text="")
            except:
                raise Exception("The input is empty")
            
        def peek_prev() -> Token:
            try:
                if pos - 1 >= 0:
                    return tokens[pos - 1]
                else:
                    return Token(loc=tokens[-1].loc, type="end", text="")
            except:
                raise Exception("The input is empty")
            
        def consume(expected: str | list[str] | None = None) -> Token:
            nonlocal pos
            token = peek()
            if isinstance(expected, str) and token.text != expected:
                raise Exception(f"{token.loc}: expected '{expected}'")
            if isinstance(expected, list) and token.text not in expected:
                comma_separated = ", ".join([f"'{e}'" for e in expected])
                raise Exception(f"{token.loc}: expected one of {comma_separated}")
            pos += 1
            return token
        
        def parse_int_literal() -> ast.Literal:
            if peek().type != "int_literal":
                raise Exception(f"{peek().loc}: expected an integer literal")
            token = consume()
            return ast.Literal(loc=token.loc, value=int(token.text))
        
        def parse_identifier() -> ast.Identifier:
            if peek().type != "identifier":
                raise Exception(f"{peek().loc}: expected an identifier")
            token = consume()
            return ast.Identifier(token.loc, token.text)

        def parse_unary(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            if peek().text == "not":
                operator = "not"
            else:
                operator = "-"
            location = peek().loc
            operators = []
            while peek().text == operator:
                operators.append(consume(operator).text)
            factor = parse_factor(allowed, allow_all)
            if len(operators) > 0:
                factor = ast.Unary(location, operators, factor)
            return factor
        
        def parse_boolean_literal() -> ast.Boolean_literal:
            token = consume()
            return ast.Boolean_literal(token.loc, token.text)
        
        def parse_factor(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            if peek().text == "(":
                return parse_parenthesized(allowed, allow_all)
            elif peek().text == "{":
                return parse_block()
            elif peek().text == "if":
                return parse_if_clause(allowed, allow_all)
            elif peek().text == "var":
                raise Exception(f"{peek().loc}: variable declaration only allowed in blocks or top-level")
            elif peek().text in ["true", "false"]:
                return parse_boolean_literal()
            elif peek().text == "while":
                return parse_while_loop(allowed, allow_all)
            elif peek().type == "int_literal":
                return parse_int_literal()
            elif peek().type == "identifier":
                return parse_identifier()
            else: 
                #print(tokens[pos:])
                raise Exception(f"{peek().loc}: expected an integer literal or and identifier")

        def parse_all():
            expressions = []
            ast_tree = None
            expressions.append(parse_expression_top([";", "ending"]))
            while peek().text == ";" or peek_prev().text == "}":
                if peek().text == ";":
                    consume(";")
                if peek().type == "end":
                    break
                expressions.append(parse_expression_top([";", "ending"]))
            if peek_prev().text == ";":
                ast_tree = ast.Block(peek_prev().loc, expressions, None)
            else:
                ast_tree = ast.Block(peek_prev().loc, expressions[:-1], expressions[-1])
            return ast_tree

        def parse_expression_top(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            if peek().text == "var":
                location = peek().loc
                consume("var")
                declaration = parse_expression([":"] + allowed, allow_all)
                if peek().text == ":":
                    consume(":")
                    typed = parse_type_expression()
                    consume("=")
                    dec_val = parse_expression(allowed, allow_all)
                    return ast.Declaration(location, declaration, dec_val, typed)
                return ast.Declaration(location, declaration.left, declaration.right, None)
            else:
                return parse_expression(allowed, allow_all)

        def parse_type_expression(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            if peek().text == "(":
                location = peek().loc
                consume("(")
                parameters = []
                param = parse_type_expression([",", ")"] + allowed, allow_all)
                parameters.append(param)
                while peek().text == ",":
                    param = parse_type_expression([",", ")"] + allowed, allow_all)
                    parameters.append(param)
                consume(")")
                consume("=>")
                result = parse_type_expression(allowed, allow_all)
                return ast.FunctionTypeExpression(loc=location, variable_types=parameters, result_type=result)
            else:
                type_expression = parse_identifier()
                if type_expression.name == "Int":
                    return Int
                elif type_expression.name == "Bool":
                    return Bool
                elif type_expression.name == "Unit":
                    return Unit
                else:
                    raise Exception(f"Invalid type: {type_expression.name}. Must be either Int, Bool or Unit.")
            
        def parse_while_loop(allowed: list[str] = [], allow_all: bool = False) -> ast.While_loop:
            location = peek().loc
            consume("while")
            cond = parse_expression(["do"] + allowed, allow_all)
            consume("do")
            itering = parse_expression(allowed, allow_all)
            return ast.While_loop(location, cond, itering)


        def parse_expression(allowed: list[str] = [], allow_all: bool = False) -> ast.BinaryOp:
            precedence = 0
            left = parse_term_precedence(precedence + 1, allowed, allow_all)
            while peek().text in left_associative_binary_operators[precedence]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_term_precedence(precedence + 1, allowed, allow_all)
                left = ast.BinaryOp(
                    left.loc,
                    left,
                    operator,
                    right
                )
            if peek().text == "=":
                operator_token = consume()
                operator = operator_token.text
                right = parse_expression(allowed, allow_all)
                left = ast.BinaryOp(
                    left.loc,
                    left,
                    operator,
                    right
                )
            if peek().type != "end" and peek().text not in allowed and not allow_all and peek_prev().text != "}":
                raise Exception(f"{peek().loc}: unexpected term: {peek().text}")
            return left
        
        def parse_term_precedence(precedence: int, allowed: list[str] = [], allow_all: bool = False) -> ast.BinaryOp:
            if precedence == len(left_associative_binary_operators) - 1:
                left = parse_term(allowed, allow_all)
            else:
                left = parse_term_precedence(precedence + 1, allowed, allow_all)
            while peek().text in left_associative_binary_operators[precedence]:
                operator_token = consume()
                operator = operator_token.text
                if precedence == len(left_associative_binary_operators) - 1:
                    right = parse_term(allowed, allow_all)
                else:
                    right = parse_term_precedence(precedence + 1, allowed, allow_all)
                left = ast.BinaryOp(
                    left.loc,
                    left,
                    operator,
                    right
                )
            return left
        
        def parse_term(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            left = parse_unary(allowed, allow_all)
            if peek().text == "(":
                arguments = parse_function(allowed, allow_all)
                left = ast.Function(left.loc, left, arguments)
            while peek().text in ["*", "/"]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_unary(allowed, allow_all)
                left = ast.BinaryOp(
                    left.loc,
                    left,
                    operator,
                    right
                )
            return left
        
        def parse_parenthesized(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            consume("(")
            expr = parse_expression([")"] + allowed, allow_all)
            consume(")")
            return expr
        
        def parse_if_clause(allowed: list[str] = [], allow_all: bool = False) -> ast.Expression:
            location = peek().loc
            consume("if")
            expr = parse_expression(["then"] + allowed, allow_all)
            consume("then")
            then_expr = parse_expression(["else"] + allowed, allow_all)
            if peek().text == "else":
                consume("else")
                else_expr = parse_expression(allowed, allow_all)
            else:
                else_expr = None
            return ast.IfExpression(location, expr, then_expr, else_expr)
        
        def parse_function(allowed: list[str] = [], allow_all: bool = False) -> list[ast.Expression]:
            arguments = []
            consume("(")
            if peek().text != ")":
                arguments.append(parse_expression([",", ")"] + allowed, allow_all))
                while peek().text == ",":
                    consume(",")
                    arguments.append(parse_expression([",", ")"] + allowed, allow_all))
            consume(")")
            return arguments
            

        def parse_block() -> ast.Block:
            location = peek().loc
            consume("{")
            sequence = []
            result = None
            if peek().text != "}":
                line = parse_expression_top([";", "}"], True)
                if peek().text not in [";", "}"] and not isinstance(line, ast.Block) and not peek_prev().text == "}":
                    raise Exception(f"Missing semicolon at {peek().loc}")
                if peek().text != "}":
                    while peek().text == ";" or isinstance(line, ast.Block) or peek_prev().text == "}":
                        print(peek().text, peek_prev().text)
                        try:
                            consume(";")
                        except:
                            pass
                        sequence.append(line)
                        if peek().text != "}":
                            line = parse_expression_top([";", "}"], True)
                            if peek().text == "}":
                                result = line
                                break
                        else:
                            break
                else:
                    result = line
            try:
                consume("}")
            except:
                raise Exception(f"Missing semicolon at {peek().loc}")
            if not result:
                result = ast.Literal(None, None)
            return ast.Block(location, sequence, result)
        
        return parse_all()
    
if __name__ == "__main__":
    P = Parser()
    code = [Token(L, "identifier", "a"), Token(L, "punctuation", ";")]

    print(P.parse(code))
    