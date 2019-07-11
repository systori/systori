"""
    Contains parsers and evaluators for expressions in a spreadsheet cell
"""
import parsec as p
import re


class Cell:
    def __init__(self, text, row: int, column: int):
        self.text = text
        self.row = row
        self.column = column


success = lambda value: p.Parser(lambda s, index: p.Value.success(index, value))

lexeme = lambda parser: parser << p.spaces()
token = lambda s: p.desc(lexeme(p.string(s)), f"{s} token")
rec = lambda fn: fn()


class ParseEquation:

    parens = lambda parser: token("(").bind(lambda _: parser.skip(token(")")))
    mul = token("*")
    div = token("/")
    plus = token("+")
    minus = token("-")

    sign = lambda _: p.desc((p.optional(p.string("-") | p.string("+"), "")), "sign")

    digits = p.desc(p.one_of("1234567890."), "digit")

    decimal = p.desc(
        (lexeme(sign) + p.many1(digits)).parsecmap(parse_decimal), "decimal"
    )

    addop = plus.parsecmap(lambda x, y: x + y) | minus.parsecmap(lambda x, y: x - y)
    mulop = mul.parsecmap(lambda x, y: x * y) | div.parsecmap(lambda x, y: x / y)

    def term(self):
        return p.separated(rec(self.atom), self.mulop, 1, 1, False)

    def expr(self):
        return p.separated(rec(self.term), self.addop, 1, 1, False)

    def atom(self):
        return p.desc(lexeme(self.decimal) | self.parens(rec(self.expr)), "atom")

    def parse_decimal(self, sign, digits):
        pass
