from dataclasses import dataclass
from typing import Literal
from objects.source_location import Source_location
from assets.test_source import L

TokenType = Literal["int_literal", "identifier", "operator", "punctuation", "end"]

@dataclass
class Token:
    loc: Source_location
    type: TokenType
    text: str

    def __eq__(self, other):
        if self.type == other.type and self.text == other.text:
            if self.loc == L or other.loc == L:
                return True
            elif self.loc == other.loc:
                return True