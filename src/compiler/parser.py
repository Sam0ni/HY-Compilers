from objects.token import Token
import objects.ast as ast
from assets.test_source import L

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
            return ast.Literal(int(token.text))
        
        def parse_identifier() -> ast.Identifier:
            if peek().type != "identifier":
                raise Exception(f"{peek().loc}: expected an identifier")
            token = consume()
            return ast.Identifier(token.text)

        def parse_unary() -> ast.Expression:
            if peek().text == "not":
                operator = "not"
            else:
                operator = "-"
            operators = []
            while peek().text == operator:
                operators.append(consume(operator).text)
            factor = parse_factor()
            if len(operators) > 0:
                factor = ast.Unary(operators, factor)
            return factor
        
        def parse_factor() -> ast.Expression:
            if peek().text == "(":
                return parse_parenthesized()
            elif peek().text == "{":
                return parse_block()
            elif peek().text == "if":
                return parse_if_clause()
            elif peek().type == "int_literal":
                return parse_int_literal()
            elif peek().type == "identifier":
                return parse_identifier()
            else: raise Exception(f"{peek().loc}: expected an integer literal or and identifier")
        
        def parse_expression(allowed: list[str] = []) -> ast.BinaryOp:
            precedence = 0
            left = parse_term_precedence(precedence + 1)
            while peek().text in left_associative_binary_operators[precedence]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_term_precedence(precedence + 1)
                left = ast.BinaryOp(
                    left,
                    operator,
                    right
                )
            if peek().text == "=":
                operator_token = consume()
                operator = operator_token.text
                right = parse_expression(allowed)
                left = ast.BinaryOp(
                    left,
                    operator,
                    right
                )
            if peek().type != "end" and peek().text not in allowed:
                raise Exception(f"{peek().loc}: unexpected term: {peek().text}")
            return left
        
        def parse_term_precedence(precedence: int) -> ast.BinaryOp:
            if precedence == len(left_associative_binary_operators) - 1:
                left = parse_term()
            else:
                left = parse_term_precedence(precedence + 1)
            while peek().text in left_associative_binary_operators[precedence]:
                operator_token = consume()
                operator = operator_token.text
                if precedence == len(left_associative_binary_operators) - 1:
                    right = parse_term()
                else:
                    right = parse_term_precedence(precedence + 1)
                left = ast.BinaryOp(
                    left,
                    operator,
                    right
                )
            return left
        
        def parse_term() -> ast.Expression:
            left = parse_unary()
            if peek().text == "(":
                arguments = parse_function()
                left = ast.Function(left, arguments)
            while peek().text in ["*", "/"]:
                operator_token = consume()
                operator = operator_token.text
                right = parse_unary()
                left = ast.BinaryOp(
                    left,
                    operator,
                    right
                )
            return left
        
        def parse_parenthesized() -> ast.Expression:
            consume("(")
            expr = parse_expression([")"])
            consume(")")
            return expr
        
        def parse_if_clause() -> ast.Expression:
            consume("if")
            expr = parse_expression(["then"])
            consume("then")
            then_expr = parse_expression(["else"])
            if peek().text == "else":
                consume("else")
                else_expr = parse_expression()
            else:
                else_expr = None
            return ast.IfExpression(expr, then_expr, else_expr)
        
        def parse_function() -> list[ast.Expression]:
            arguments = []
            consume("(")
            arguments.append(parse_expression([",", ")"]))
            while peek().text == ",":
                consume(",")
                arguments.append(parse_expression([",", ")"]))
            consume(")")
            return arguments
            

        def parse_block() -> ast.Block:
            consume("{")
            sequence = []
            result = None
            if peek().text != "}":
                try:
                    line = parse_expression([";", "}"])
                except:
                    raise Exception(f"Missing semicolon at {peek().loc}")
                while peek().text == ";":
                    consume(";")
                    sequence.append(line)
                    if peek().text != "}":
                        print(peek().text)
                        line = parse_expression([";", "}"])
                        if peek().text == "}":
                            result = line
                            break
            consume("}")
            if result == None:
                result = ast.Literal(None)
            return ast.Block(sequence, result)
            
        
        return parse_expression()
    
if __name__ == "__main__":
    P = Parser()
    if_clause = [Token(L, "punctuation", "{"), Token(L, "identifier", "f"), Token(L, "punctuation", "("), Token(L, "identifier", "a"), Token(L, "punctuation", ")"), Token(L, "identifier", "x"), Token(L, "operator", "="), Token(L, "identifier", "3"), Token(L, "punctuation", ";"), Token(L, "punctuation", "}")]
    print(P.parse(if_clause))