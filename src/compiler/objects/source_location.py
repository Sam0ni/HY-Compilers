from dataclasses import dataclass

@dataclass
class Source_location:
    file: str
    line: int
    column: int

    def __eq__(self, other):
        if self.file == other.file and self.line == other.line and self.column == other.column:
            return True