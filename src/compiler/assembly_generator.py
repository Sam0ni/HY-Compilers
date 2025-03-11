import compiler.objects.ir_variables as ir
import compiler.objects.ir_instructions as iri
import dataclasses
from compiler.objects.locals import Locals
from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from compiler.typechecker import typechecker
from compiler.ir_generator import generate_ir
from compiler.objects.node_types import Type, BasicType, Bool, Int, Unit, FunType
from compiler.assets.intrinsics import all_intrinsics, IntrinsicArgs


def get_all_ir_variables(instructions: list[iri.Instruction]) -> list[ir.IRVar]:
    operators = ["==", "!=", "<=", ">=", "=>", "<", ">", "+", "-", "*", "/", "=", "%", "unary_not", "unary_-"]
    built_in = ["print_int", "print_bool", "read_int"]
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set and v.name not in operators and v.name not in built_in:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list

def generate_assembly(instructions: list[iri.Instruction]) -> str:
    lines = []
    operators = ["==", "!=", "<=", ">=", "=>", "<", ">", "+", "-", "*", "/", "=", "%", "unary_not", "unary_-"]
    def emit(line: str) -> None: lines.append(line)

    locals = Locals(
        variables=get_all_ir_variables(instructions)
    )

    # ... Emit initial declarations and stack setup here ...
    initial_declarations = [f".extern print_int",
    f".extern print_bool",
    f".extern read_int",
    f".global main",
    f".type main, @function",
    f".section .text",
    f"main:",
    f"pushq %rbp",
    f"movq %rsp, %rbp",
    f"subq ${locals.stack_used()}, %rsp"]
    for dec in initial_declarations:
        emit(dec)

    for insn in instructions:
        emit('# ' + str(insn))
        match insn:
            case iri.Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
            case iri.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case iri.Jump():
                emit(f'jmp .L{insn.label.name}')

            case iri.LoadBoolConst():
                if insn.value == "true":
                    val = 1
                else:
                    val = 0
                emit(f"movq ${val}, {locals.get_ref(insn.dest)}")

            case iri.Copy():
                emit(f"movq {locals.get_ref(insn.source)}, %rax")
                emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case iri.CondJump():
                emit(f"cmpq $0, {locals.get_ref(insn.cond)}")
                emit(f"jne .L{insn.then_label.name}")
                emit(f"jmp .L{insn.else_label.name}")

            case iri.Call():
                if insn.fun.name in operators:
                    args = list(map(locals.get_ref, insn.args))
                    all_intrinsics[insn.fun.name](IntrinsicArgs(args, f"%rax", emit))
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")
                else:
                    registers_used = 0
                    registers = [f"%rdi", f"%rsi", f"%rdx", f"%rcx", f"%r8", f"%r9"]
                    pushed = 0
                    correction = False
                    if locals.stack_used() % 16 != 0:
                        emit(f"subq $8, %rsp")
                        correction = True
                    for arg in insn.args[:6]:
                        emit(f"movq {locals.get_ref(arg)}, {registers[registers_used]}")
                        registers_used += 1
                    for arg in insn.args[-1:registers_used:-1]:
                        emit(f"pushq {locals.get_ref(arg)}")
                        pushed += 1
                    emit(f"callq {insn.fun.name}")
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")
                    if pushed > 0:
                        emit(f"addq ${8*pushed}, %rsp")
                    if correction:
                        emit(f"addq $8, %rsp")
                
                
        
    post_stack = [f"movq %rbp, %rsp", f"popq %rbp", f"ret"]
    for dec in post_stack:
        emit(dec)
    
    return "\n".join(lines)


if __name__ == "__main__":
    tok = Tokenizer()
    par = Parser()
    inp = par.parse(tok.tokenize("print_int(2)"))
    typechecker(inp)
    rt_types = {ir.IRVar("+"): FunType([Int, Int], Int), ir.IRVar("*"): FunType([Int, Int], Int), ir.IRVar("print_int"): FunType([Int], Unit), ir.IRVar("print_bool"): FunType([Bool], Unit), ir.IRVar("unary_not"): FunType([Bool], Bool), ir.IRVar("unary_-"): FunType([Int], Int), ir.IRVar("<"): FunType([Int, Int], Bool), ir.IRVar(">"): FunType([Int, Int], Bool), ir.IRVar("<="): FunType([Int, Int], Bool), ir.IRVar(">="): FunType([Int, Int], Bool), ir.IRVar("-"): FunType([Int, Int], Int), ir.IRVar("/"): FunType([Int, Int], Int), ir.IRVar("%"): FunType([Int, Int], Int), ir.IRVar("=="): FunType([BasicType, BasicType], Bool), ir.IRVar("!="): FunType([BasicType, BasicType], Bool)}
    all_ir = generate_ir(rt_types, inp)
    print(generate_assembly(all_ir))