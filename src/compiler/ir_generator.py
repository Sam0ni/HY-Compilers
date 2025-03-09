from objects.ir_variables import IRVar
from objects.node_types import Type, BasicType, Bool, Int, Unit, FunType
import objects.ir_instructions as ir
import objects.ast as ast
from objects.sym_table import SymTab
from tokenizer import Tokenizer
from parser import Parser
from typechecker import typechecker

def generate_ir(
    # 'root_types' parameter should map all global names
    # like 'print_int' and '+' to their types.
    root_types: dict[IRVar, Type],
    nodes: list[ast.Expression]
) -> list[ir.Instruction]:
    cur_var_num = 1
    cur_lab_num = 1
    var_types: dict[IRVar, Type] = root_types.copy()

    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    def new_var(t: Type) -> IRVar:
        # Create a new unique IR variable and
        # add it to var_types
        nonlocal cur_var_num
        new_var_name = "x" + str(cur_var_num)
        cur_var_num += 1
        new_one = IRVar(new_var_name)
        var_types[new_one] = t
        return new_one
    
    def new_label(loc) -> ir.Label:
        nonlocal cur_lab_num
        new_lab_name = "L" + str(cur_lab_num)
        cur_lab_num += 1
        new_one = ir.Label(loc, new_lab_name)
        return new_one

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(st: SymTab, expr: ast.Expression) -> IRVar:
        loc = expr.loc

        def equals_handle(st: SymTab, expr: ast.Expression):
            var_val = visit(st, expr.right)
            var_org = st.require(expr.left)
            ins.append(ir.Copy(var_val, var_org))
            return var_org
        
        def short_circuit(st: SymTab, expr: ast.Expression):
            if expr.op == "or":
                l_right = new_label(loc)
                l_skip = new_label(loc)
                l_end = new_label(loc)
                var_left = visit(st, expr.left)
                var_right = visit(st, expr.right)
                var_result = new_var(Bool)
                ins.append(ir.CondJump(loc, var_left, l_skip, l_right))
                ins.append(l_right)
                ins.append(ir.Copy(loc, var_right, var_result))
                ins.append(ir.Jump(loc, l_end))
                ins.append(l_skip)
                ins.append(ir.LoadBoolConst(loc, "true", var_result))
                ins.append(ir.Jump(l_end))
                ins.append(l_end)
            else:
                l_right = new_label(loc)
                l_skip = new_label(loc)
                l_end = new_label(loc)
                var_left = visit(st, expr.left)
                var_right = visit(st, expr.right)
                var_result = new_var(Bool)
                ins.append(ir.CondJump(loc, var_left, l_right, l_skip))
                ins.append(l_right)
                ins.append(ir.Copy(loc, var_right, var_result))
                ins.append(ir.Jump(loc, l_end))
                ins.append(l_skip)
                ins.append(ir.LoadBoolConst(loc, "false", var_result))
                ins.append(ir.Jump(l_end))
                ins.append(l_end)
            return var_result

        match expr:
            case ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(ir.LoadBoolConst(
                            loc, expr.value, var))
                    case int():
                        var = new_var(Int)
                        ins.append(ir.LoadIntConst(
                            loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return st.require(expr.name)
            
            case ast.Boolean_literal():
                var = new_var(Bool)
                ins.append(ir.LoadBoolConst(loc, expr.boolean, var))
                return var
            
            case ast.BinaryOp():
                # Ask the symbol table to return the variable that refers
                # to the operator to call.
                if expr.op == "=":
                    return equals_handle(st, expr)
                elif expr.op in ["and", "or"]:
                    return short_circuit(st, expr)
                var_op = st.require(expr.op)
                # Recursively emit instructions to calculate the operands.
                var_left = visit(st, expr.left)
                var_right = visit(st, expr.right)
                # Generate variable to hold the result.
                var_result = new_var(expr.type)
                # Emit a Call instruction that writes to that variable.
                ins.append(ir.Call(
                    loc, var_op, [var_left, var_right], var_result))
                return var_result
            
            
            case ast.IfExpression():
                if expr.else_clause is None:
                    # Create (but don't emit) some jump targets.
                    l_then = new_label(loc)
                    l_end = new_label(loc)

                    # Recursively emit instructions for
                    # evaluating the condition.
                    var_cond = visit(st, expr.cond)
                    # Emit a conditional jump instruction
                    # to jump to 'l_then' or 'l_end',
                    # depending on the content of 'var_cond'.
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    # Emit the label that marks the beginning of
                    # the "then" branch.
                    ins.append(l_then)
                    # Recursively emit instructions for the "then" branch.
                    visit(st, expr.then_clause)

                    # Emit the label that we jump to
                    # when we don't want to go to the "then" branch.
                    ins.append(l_end)

                    # An if-then expression doesn't return anything, so we
                    # return a special variable "unit".
                    return var_unit
                else:
                    l_then = new_label(loc)
                    l_else = new_label(loc)
                    l_end = new_label(loc)
                    var_result = new_var(expr.then_clause.type)

                    var_cond = visit(st, expr.cond)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_else))
                    # then
                    ins.append(l_then)
                    var_then = visit(st, expr.then_clause)
                    ins.append(ir.Copy(loc, var_then, var_result))
                    ins.append(ir.Jump(loc, l_end))
                    # else
                    ins.append(l_else)
                    var_else = visit(st, expr.else_clause)
                    ins.append(ir.Copy(loc, var_else, var_result))
                    ins.append(l_end)
                    
                    return var_result

            case ast.Function():
                if st.require(expr.name):
                    args = []
                    for arg in expr.arguments:
                        args.append(visit(arg))
                    var_result = new_var(rt_types[st.require(expr.name)].result_type)
                    ins.append(ir.Call(loc, st.require(expr.name), args, var_result))
                    return var_result
                else:
                    raise Exception(f"No such function as {expr.name}")

            case ast.Unary():
                if expr.operators[0] == "not":
                    if not isinstance(expr.exp, ast.Boolean_literal):
                        raise Exception(f"{expr.exp} not a boolean")
                    bool_var = visit(st, expr.exp)
                    vars = []
                    for op in expr.operators:
                        vars.append(new_var(Bool))
                        ins.append(ir.Call(loc, st.require("unary_not"), [bool_var], vars[-1]))
                        bool_var = vars[-1]
                    return bool_var
                else:
                    if not isinstance(expr.exp, ast.Literal) and isinstance(expr.exp.value, int):
                        raise Exception(f"{expr.exp} not an integer")
                    int_var = visit(st, expr.exp)
                    vars = []
                    for op in expr.operators:
                        vars.append(new_var(Int))
                        ins.append(ir.Call(loc, st.require("unary_-"), [int_var], vars[-1]))
                        int_var = vars[-1]
                    return int_var
                
            case ast.Block():
                new_scope = SymTab({}, st)
                if len(expr.sequence) == 0 and expr.result == None:
                    return var_unit
                for seq in expr.sequence:
                    visit(new_scope, seq)
                if expr.result is None:
                    return var_unit
                else: 
                    return visit(new_scope, expr.result)
            
            case ast.Declaration():
                var_val = visit(st, expr.value)
                var_result = new_var(var_types[var_val])
                ins.append(ir.Copy(loc, var_val, var_result))
                st.variables[expr.variable.name] = var_result
                return var_unit
                
            
            case ast.While_loop():
                l_start = new_label(loc)
                l_body = new_label(loc)
                l_end = new_label(loc)

                var_cond = visit(st, expr.condition)

                ins.append(l_start)
                ins.append(ir.CondJump(loc, var_cond, l_body, l_end))
                ins.append(l_body)
                visit(st, expr.itering)
                ins.append(ir.Jump(loc, l_start))
                ins.append(l_end)
                return var_unit
                    
            #... # Other AST node cases (see below)

    # Convert 'root_types' into a SymTab
    # that maps all available global names to
    # IR variables of the same name.
    # In the Assembly generator stage, we will give
    # definitions for these globals. For now,
    # they just need to exist.
    root_symtab = SymTab({})
    for v in root_types.keys():
        root_symtab.add_local(v.name, v)


    for root_expr in nodes:
        # Start visiting the AST from the root.
        var_final_result = visit(root_symtab, root_expr)

    locat = nodes[-1].loc

    if var_types[var_final_result] == Int:
        dest_var = new_var(Int)
        ins.append(ir.Call(locat, root_symtab.require("print_int"), [var_final_result], dest_var))
    elif var_types[var_final_result] == Bool:
        dest_var = new_var(Bool)
        ins.append(ir.Call(locat, root_symtab.require("print_bool"), [var_final_result], dest_var))

    return ins


if __name__ == "__main__":
    tok = Tokenizer()
    par = Parser()
    inp = par.parse(tok.tokenize("1 == 2"))
    typechecker(inp)
    rt_types = {IRVar("+"): FunType([Int, Int], Int), IRVar("*"): FunType([Int, Int], Int), IRVar("print_int"): FunType([Int], Unit), IRVar("print_bool"): FunType([Bool], Unit), IRVar("unary_not"): FunType([Bool], Bool), IRVar("unary_-"): FunType([Int], Int), IRVar("<"): FunType([Int, Int], Bool), IRVar(">"): FunType([Int, Int], Bool), IRVar("<="): FunType([Int, Int], Bool), IRVar(">="): FunType([Int, Int], Bool), IRVar("-"): FunType([Int, Int], Int), IRVar("/"): FunType([Int, Int], Int), IRVar("%"): FunType([Int, Int], Int), IRVar("=="): FunType([BasicType, BasicType], Bool), IRVar("!="): FunType([BasicType, BasicType], Bool)}
    print(generate_ir(rt_types, inp))