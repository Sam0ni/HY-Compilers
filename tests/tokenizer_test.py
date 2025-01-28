from compiler.tokenizer import Tokenizer
from compiler.assets.test_source import L
from compiler.objects.token import Token
from compiler.objects.source_location import Source_location
tokenize = Tokenizer.tokenize

def test_tokenizer_basics() -> None:
    assert tokenize("if  3\nwhile") == [Token(loc=Source_location("if  3\nwhile", 1, 1), type="identifier", text="if"),
Token(loc=Source_location("if  3\nwhile", 1, 5), type="int_literal", text="3"),
Token(loc=Source_location("if  3\nwhile", 2, 1), type="identifier", text="while")]

def test_no_negative_integers() -> None:
    assert tokenize("if -344 and Y1ppee") == [Token(loc=Source_location("if -344 and Y1ppee", 1, 1), type="identifier", text="if"),
Token(loc=Source_location("if -344 and Y1ppee", 1, 4), type="operator", text="-"),
Token(loc=Source_location("if -344 and Y1ppee", 1, 5), type="int_literal", text="344"),
Token(loc=Source_location("if -344 and Y1ppee", 1, 9), type="identifier", text="and"), Token(loc=Source_location("if -344 and Y1ppee", 1, 13), type="identifier", text="Y1ppee")]

def test_identifiers_work() -> None:
    assert tokenize("if _He123 H_E_L_L_0") == [Token(loc=Source_location("if _He123 H_E_L_L_0", 1, 1), type="identifier", text="if"),
Token(loc=Source_location("if _He123 H_E_L_L_0", 1, 4), type="identifier", text="_He123"),
Token(loc=Source_location("if _He123 H_E_L_L_0", 1, 11), type="identifier", text="H_E_L_L_0")]
    
def test_punctuations_work() -> None:
    assert tokenize("(){},;") == [Token(loc=L, type="punctuation", text="("), Token(loc=L, type="punctuation", text=")"), Token(loc=L, type="punctuation", text="{"), Token(loc=L, type="punctuation", text="}"), Token(loc=L, type="punctuation", text=","), Token(loc=L, type="punctuation", text=";")]

def test_operators_work() -> None:
    assert tokenize("==<=>==!=<>+-/*") == [Token(loc=L, type="operator", text="=="),
                                           Token(loc=L, type="operator", text="<="),
                                           Token(loc=L, type="operator", text=">="),
                                           Token(loc=L, type="operator", text="="),
                                           Token(loc=L, type="operator", text="!="),
                                           Token(loc=L, type="operator", text="<"),
                                           Token(loc=L, type="operator", text=">"),
                                           Token(loc=L, type="operator", text="+"),
                                           Token(loc=L, type="operator", text="-"),
                                           Token(loc=L, type="operator", text="/"),
                                           Token(loc=L, type="operator", text="*"),]
    
def test_oneline_comments_are_skipped() -> None:
    assert tokenize("// this is comment \n # this is another comment  \nthisshouldremain") == [Token(loc=Source_location("// this is comment \n # this is another comment  \nthisshouldremain", 3, 1), type="identifier", text="thisshouldremain")]

def test_multiline_comments_are_skipped() -> None:
    assert tokenize("/* \n this \n is \n comment */ \nthisremains") == [Token(loc=Source_location("/* \n this \n is \n comment */ \nthisremains", 5, 1), type="identifier", text="thisremains")]