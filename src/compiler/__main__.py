from base64 import b64encode
import json
import re
import sys
from socketserver import ForkingTCPServer, StreamRequestHandler
from traceback import format_exception
from typing import Any
from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from compiler.typechecker import typechecker
from compiler.ir_generator import generate_ir
from compiler.assembly_generator import generate_assembly
from compiler.objects.node_types import Type, BasicType, Bool, Int, Unit, FunType
import compiler.objects.ir_variables as ir
from compiler.assembler import assemble_and_get_executable


def call_compiler(source_code: str, input_file_name: str) -> bytes:
    # *** TODO ***
    # Call your compiler here and return the compiled executable.
    # Raise an exception on compilation error.
    #
    # The input file name is informational only: you can optionally include in your source locations and error messages,
    # or you can ignore it.
    # *** TODO ***
    tok = Tokenizer()
    par = Parser()
    print(tok.tokenize(source_code, input_file_name))
    inp = par.parse(tok.tokenize(source_code, input_file_name))
    typechecker(inp)
    rt_types = {ir.IRVar("+"): FunType([Int, Int], Int), ir.IRVar("*"): FunType([Int, Int], Int), ir.IRVar("print_int"): FunType([Int], Unit), ir.IRVar("print_bool"): FunType([Bool], Unit), ir.IRVar("read_int"): FunType([], Int), ir.IRVar("unary_not"): FunType([Bool], Bool), ir.IRVar("unary_-"): FunType([Int], Int), ir.IRVar("<"): FunType([Int, Int], Bool), ir.IRVar(">"): FunType([Int, Int], Bool), ir.IRVar("<="): FunType([Int, Int], Bool), ir.IRVar(">="): FunType([Int, Int], Bool), ir.IRVar("-"): FunType([Int, Int], Int), ir.IRVar("/"): FunType([Int, Int], Int), ir.IRVar("%"): FunType([Int, Int], Int), ir.IRVar("=="): FunType([BasicType, BasicType], Bool), ir.IRVar("!="): FunType([BasicType, BasicType], Bool)}
    all_ir = generate_ir(rt_types, inp)
    assembly = generate_assembly(all_ir)
    print(assembly)
    return assemble_and_get_executable(assembly)



def main() -> int:
    # === Option parsing ===
    command: str | None = None
    input_file: str | None = None
    output_file: str | None = None
    host = "127.0.0.1"
    port = 3000
    for arg in sys.argv[1:]:
        if (m := re.fullmatch(r'--output=(.+)', arg)) is not None:
            output_file = m[1]
        elif (m := re.fullmatch(r'--host=(.+)', arg)) is not None:
            host = m[1]
        elif (m := re.fullmatch(r'--port=(.+)', arg)) is not None:
            port = int(m[1])
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    if command is None:
        print(f"Error: command argument missing", file=sys.stderr)
        return 1

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    # === Command implementations ===

    if command == 'compile':
        source_code = read_source_code()
        if output_file is None:
            raise Exception("Output file flag --output=... required")
        executable = call_compiler(source_code, input_file or '(source code)')
        with open(output_file, 'wb') as f:
            f.write(executable)
    elif command == 'serve':
        try:
            run_server(host, port)
        except KeyboardInterrupt:
            pass
    else:
        print(f"Error: unknown command: {command}", file=sys.stderr)
        return 1
    return 0


def run_server(host: str, port: int) -> None:
    class Server(ForkingTCPServer):
        allow_reuse_address = True
        request_queue_size = 32

    class Handler(StreamRequestHandler):
        def handle(self) -> None:
            result: dict[str, Any] = {}
            try:
                input_str = self.rfile.read().decode()
                input = json.loads(input_str)
                if input["command"] == "compile":
                    source_code = input["code"]
                    executable = call_compiler(source_code, "(source code)")
                    result["program"] = b64encode(executable).decode()
                elif input["command"] == "ping":
                    pass
                else:
                    result["error"] = "Unknown command: " + input['command']
            except Exception as e:
                result["error"] = "".join(format_exception(e))
            result_str = json.dumps(result)
            self.request.sendall(str.encode(result_str))

    print(f"Starting TCP server at {host}:{port}")
    with Server((host, port), Handler) as server:
        server.serve_forever()


if __name__ == '__main__':
    sys.exit(main())
