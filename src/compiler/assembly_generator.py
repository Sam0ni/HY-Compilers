import objects.ir_variables as ir
import objects.ir_instructions as iri
import dataclasses
from objects.locals import Locals
from tokenizer import Tokenizer
from parser import Parser
from typechecker import typechecker
from ir_generator import generate_ir
from objects.node_types import Type, BasicType, Bool, Int, Unit, FunType


def get_all_ir_variables(instructions: list[iri.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
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
                ...
        
    post_stack = [f"movq %rbp, %rsp", f"popq %rbp", f"ret"]
    for dec in post_stack:
        emit(dec)
    
    return lines


if __name__ == "__main__":
    tok = Tokenizer()
    par = Parser()
    inp = par.parse(tok.tokenize("{ var x = true; if x then 1 else 2; }"))
    typechecker(inp)
    rt_types = {ir.IRVar("+"): FunType([Int, Int], Int), ir.IRVar("*"): FunType([Int, Int], Int), ir.IRVar("print_int"): FunType([Int], Unit), ir.IRVar("print_bool"): FunType([Bool], Unit), ir.IRVar("unary_not"): FunType([Bool], Bool), ir.IRVar("unary_-"): FunType([Int], Int), ir.IRVar("<"): FunType([Int, Int], Bool), ir.IRVar(">"): FunType([Int, Int], Bool), ir.IRVar("<="): FunType([Int, Int], Bool), ir.IRVar(">="): FunType([Int, Int], Bool), ir.IRVar("-"): FunType([Int, Int], Int), ir.IRVar("/"): FunType([Int, Int], Int), ir.IRVar("%"): FunType([Int, Int], Int), ir.IRVar("=="): FunType([BasicType, BasicType], Bool), ir.IRVar("!="): FunType([BasicType, BasicType], Bool)}
    all_ir = generate_ir(rt_types, inp)
    print(generate_assembly(all_ir))