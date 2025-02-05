import objects.ast as ast
from objects.types import Int, Bool, Type
from objects.sym_table import SymTab

def typecheck(node: ast.Expression, symbols: SymTab = SymTab({}, None)) -> Type:

    match node:
        case ast.BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.op == "+":
                if t1 is not Int or t2 is not Int:
                    raise Exception(f"In {node} the operators were not of same type")
                return Int
        
        case ast.IfExpression():
            t1 = typecheck(node.cond)
            if t1 is not Bool:
                raise Exception(f"In {node} the condition is not of type Bool")
            t2 = typecheck(node.then_clause)
            t3 = typecheck(node.else_clause)
            if t2 != t3:
                raise Exception(f"In {node} then and else were not of same type")
            return t2
        
        case ast.Literal():
            if isinstance(node.value, int):
                return Int
            else:
                raise Exception(f"Unknown literal type: {node.value}")
            
        case ast.Identifier():
            if symbols:
                if node.name in symbols.variables.keys():
                    return typecheck(symbols.variables[node.name])
                current_scope = symbols.parent
                while(current_scope):
                    if node.name in current_scope.variables.keys():
                        return typecheck(current_scope.variables[node.name])
                    current_scope = current_scope.parent
            raise Exception("Variable referenced before declaration")
        
        case ast.Declaration():
            val = typecheck(node.value)
            if node.variable in symbols.variables.keys():
                raise Exception(f"{node.variable} already declared")
            symbols.variables[node.variable] = val
            return val

                    
                
            
        

if __name__ == "__main__":
    print(isinstance(None, int))