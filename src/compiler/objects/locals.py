import compiler.objects.ir_variables as ir


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._stack_used = 0
        self._var_to_location = {}
        for var in variables:
            self._stack_used += 8
            loc = f"{-self._stack_used}(%rbp)"
            self._var_to_location[var] = loc

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used