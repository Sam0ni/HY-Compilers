import compiler.objects.ast as ast
from compiler.objects.node_types import Int, Bool, Unit, Type, FunType
from compiler.objects.sym_table import SymTab

def typechecker(node: ast.Expression, top_level: SymTab = SymTab({"print_int": FunType([Int], Unit), "print_bool": FunType([Bool], Unit), "read_int": FunType([], Int)}, None)) -> Type:
    lineType = ""

    top_level_vars = top_level

    def binary_op_type(node: ast.BinaryOp, symbols: SymTab = SymTab({}, None)) -> Type:
        t1 = typecheck(node.left, symbols)
        t2 = typecheck(node.right, symbols)
        if node.op in ["+", "-", "*", "/", "%"]:
            if t1 is not Int or t2 is not Int:
                raise Exception(f"In {node} the operators were not of same type")
            return Int
        elif node.op in ["<", ">", ">=", "<="]:
            if t1 is not Int or t2 is not Int:
                raise Exception(f"In {node} the operators were not of same type")
            return Bool
        elif node.op == "=":
            if t1 != t2:
                raise Exception(f"Variable {node.left} is not of the same type as {node.right}")
            return t2
        elif node.op in ["==", "!="]:
            if t1 != t2:
                raise Exception(f"{node.left} and {node.right} are not of the same type")
            return Bool
        elif node.op in ["and", "or"]:
            if t1 is not Bool or t2 is not Bool:
                raise Exception(f"{node.left} and {node.right} are not both boolean")
            return Bool
        
    def if_expression_type(node: ast.IfExpression, symbols: SymTab = SymTab({}, None)) -> Type:
        t1 = typecheck(node.cond, symbols)
        if t1 is not Bool:
            raise Exception(f"In {node} the condition is not of type Bool")
        t2 = typecheck(node.then_clause, symbols)
        if node.else_clause:
            t3 = typecheck(node.else_clause, symbols)
            if t2 != t3:
                raise Exception(f"In {node} then and else were not of same type")
            return t2
        else:
            return Unit
        
    def literal_type(node: ast.Literal, symbols: SymTab = SymTab({}, None)) -> Type:
        if isinstance(node.value, int):
            return Int
        elif node.value == None:
            return None
        else:
            print(node)
            raise Exception(f"Unknown literal type: {node.value}")

    def identifier_type(node: ast.Identifier, symbols: SymTab = SymTab({}, None)) -> Type:
        if symbols:
            if node.name in symbols.variables.keys():
                return symbols.variables[node.name]
            current_scope = symbols.parent
            while(current_scope):
                if node.name in current_scope.variables.keys():
                    return current_scope.variables[node.name]
                current_scope = current_scope.parent
        raise Exception(f"Variable referenced before declaration")

    def declaration_type(node: ast.Declaration, symbols: SymTab = SymTab({}, None)) -> Type:
        val = typecheck(node.value, symbols)
        if node.variable.name in symbols.variables.keys():
            raise Exception(f"{node.variable.name} already declared")
        if node.typed:
            typed_type = node.typed
            if val != typed_type:
                raise Exception(f"{node.value} is not of type {typed_type}")
        symbols.variables[node.variable.name] = val
        return Unit
    
    def unary_type(node: ast.Unary, symbols: SymTab = SymTab({}, None)) -> Type:
        val = typecheck(node.exp, symbols)
        return val
    
    def boolean_literal_type(node: ast.Boolean_literal, symbols: SymTab = SymTab({}, None)) -> Type:
        if node.boolean in ["true", "false"]:
            return Bool
        
    def function_type(node: ast.Function, symbols: SymTab = SymTab({}, None)) -> Type:
        parameter_types = []
        for par in node.arguments:
            parameter_types.append(typecheck(par, symbols))
        res = typecheck(node.name, symbols)
        if isinstance(res, FunType):
            for i in range(len(res.parameter_types)):
                if parameter_types[i] != res.parameter_types[i]:
                    raise Exception(f"Wrong parametertype for function {node.name.name}")
            return res.result_type
        return FunType(parameter_types, res)

    def block_type(node: ast.Block, symbols: SymTab = SymTab({}, None)) -> Type:
        new_level = SymTab({}, symbols)
        if len(node.sequence) == 0 and not node.result:
            return Unit
        for i in node.sequence:
            typecheck(i, new_level)
        if node.result is not None and not (isinstance(node.result, ast.Literal) and node.result == ast.Literal(None, None)):
            return typecheck(node.result, new_level)
        else:
            return Unit
        
    def while_loop_type(node: ast.While_loop, symbols: SymTab = SymTab({}, None)) -> Type:
        cond = typecheck(node.condition, symbols)
        if cond is not Bool:
            raise Exception(f"In {node} the condition is not of type Bool")
        return Unit

    def typecheck(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        result = None
        match node:
            case ast.BinaryOp():
                result = binary_op_type(node, symbols)
            
            case ast.IfExpression():
                result = if_expression_type(node, symbols)
            
            case ast.Literal():
                result = literal_type(node, symbols)

            case ast.Identifier():
                result = identifier_type(node, symbols)            
            
            case ast.Declaration():
                result = declaration_type(node, symbols)
            
            case ast.Unary():
                result = unary_type(node, symbols)

            case ast.Boolean_literal():
                result = boolean_literal_type(node, symbols)

            case ast.Function():
                result = function_type(node, symbols)

            case ast.Block():
                result = block_type(node, symbols)

            case ast.While_loop():
                result = while_loop_type(node, symbols)

        node.type = result
        return result
    

                
    lineType = typecheck(node, top_level_vars)

    return lineType
                
            
        

if __name__ == "__main__":
    print(isinstance(None, int))