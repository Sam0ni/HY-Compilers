import re
from compiler.objects.token import Token
from compiler.objects.source_location import Source_location

identifier_keyword_re = re.compile(r"([a-z]|[A-Z]|_)([a-z]|[A-Z]|_|[0-9])*")
integer_literal_re = re.compile(r"([1-9][0-9]*|[0-9])")
whitespace_re = re.compile(r"[ \t\r\f\v]+")
newline_re = re.compile(r"\n")
operators_re = re.compile(r"(==|!=|<=|>=|=>|<|>|\+|-|\*|/|=|%|not)")
punctuation_re = re.compile(r"(\(|\)|{|}|,|;)")
oneline_comment_re = re.compile(r"(//|#).+($|\n)")
multiline_comment_re = re.compile(r"/[*](\s|.)+?[*]/")




class Tokenizer:
    @staticmethod
    def tokenize(source_code: str, file_name: str = "tester") -> list[str]:
        tokens = []
        line = 1
        indx = 0
        column = 1
        regexes = [(identifier_keyword_re, "identifier"), (integer_literal_re, "int_literal"), (operators_re, "operator"), (punctuation_re, "punctuation")]
        
        def regex_matcher():
            nonlocal indx
            nonlocal column
            for regex in regexes:
                match = regex[0].match(source_code, indx)
                if match:
                    source = Source_location(file_name, line, column)
                    new_token = Token(source, regex[1], match.group())
                    tokens.append(new_token)
                    indx = match.end()
                    column += len(match.group())
                    return True
            return False
        
        def line_matcher():
            nonlocal indx
            nonlocal column
            nonlocal line
            line_regexes = [newline_re, oneline_comment_re]
            for regex in line_regexes:
                match = regex.match(source_code, indx)
                if match:
                    column = 1
                    line += 1
                    indx = match.end()
                    return True
            return False

        while indx < len(source_code):
            whites = whitespace_re.match(source_code, indx)
            if whites:
                indx = whites.end()
                column += len(whites.group())
                continue
            if line_matcher():
                continue
            multiline = multiline_comment_re.match(source_code, indx)
            if multiline:
                linesskips = len(newline_re.findall(source_code, indx, multiline.end()))
                line += linesskips
                indx = multiline.end()
                column = 0
                continue
            if regex_matcher():
                continue
            indx += 1
            column += 1
        tokens.append(Token(Source_location(file_name, line + 1, 0), "end", "ending"))
        return tokens


if __name__ == "__main__":
    T = Tokenizer()
    print(T.tokenize("123 # hello"))