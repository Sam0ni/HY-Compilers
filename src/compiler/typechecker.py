import objects.ast as ast
from objects.types import Int, Bool, Unit, Type, FunType
from objects.sym_table import SymTab

def typechecker(nodes: list[ast.Expression], top_level: SymTab = SymTab({}, None)) -> Type:
    lineTypes = []

    top_level_vars = top_level

    def binary_op_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        t1 = typecheck(node.left)
        t2 = typecheck(node.right)
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
                raise Exception(f"Variable {t1} is not of the same type as {t2}")
            return t2
        elif node.op in ["==", "!="]:
            if t1 != t2:
                raise Exception(f"{t1} and {t2} are not of the same type")
            return Bool
        
    def if_expression_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        t1 = typecheck(node.cond)
        if t1 is not Bool:
            raise Exception(f"In {node} the condition is not of type Bool")
        t2 = typecheck(node.then_clause)
        if node.else_clause:
            t3 = typecheck(node.else_clause)
            if t2 != t3:
                raise Exception(f"In {node} then and else were not of same type")
            return t2
        else:
            return Unit
        
    def literal_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        if isinstance(node.value, int):
            return Int
        elif node.value == None:
            return None
        else:
            print(node)
            raise Exception(f"Unknown literal type: {node.value}")

    def identifier_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        if symbols:
            if node.name in symbols.variables.keys():
                return symbols.variables[node.name]
            current_scope = symbols.parent
            while(current_scope):
                if node.name in current_scope.variables.keys():
                    return typecheck(current_scope.variables[node.name])
                current_scope = current_scope.parent
        raise Exception("Variable referenced before declaration")

    def declaration_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        val = typecheck(node.value)
        if node.variable.name in symbols.variables.keys():
            raise Exception(f"{node.variable.name} already declared")
        if node.typed:
            typed_type = node.typed
            if val != typed_type:
                raise Exception(f"{node.value} is not of type {typed_type}")
        symbols.variables[node.variable.name] = val
        return Unit
    
    def unary_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        val = typecheck(node.exp)
        return val
    
    def boolean_literal_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        if node.boolean in ["true", "false"]:
            return Bool
        
    def function_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        parameter_types = []
        for par in node.arguments:
            parameter_types.append(typecheck(par))
        res = typecheck(node.name)
        return FunType(parameter_types, res)

    def block_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        new_level = SymTab({}, symbols)
        if len(node.sequence) == 0 and not node.result:
            return Unit
        for i in node.sequence:
            typecheck(i, new_level)
        result = typecheck(node.result, new_level)
        if result:
            return result
        else:
            return Unit
        
    def while_loop_type(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:
        cond = typecheck(node.condition)
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
                

    for node in nodes:
        lineTypes.append(typecheck(node, top_level_vars))

    return lineTypes
                
            
        

if __name__ == "__main__":
    print(isinstance(None, int))