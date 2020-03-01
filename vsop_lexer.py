# -----------------------------------------------------------------------------
# vsop_lex.py
#
# VSOP Lexer
#
# REF:
#   https://www.dabeaz.com/ply/ply.html#ply_nn5
#   https://github.com/dabeaz/ply/blob/master/ply/lex.py
#   https://www.programcreek.com/python/example/101132/ply.lex.lexer
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

import ply.lex as lex
from ply.lex import TOKEN

class LexicalError(Exception):
    def __init__(self, line, column, description):
        self.line = line
        self.column = column
        self.description = description

class VsopLexer:
    states = (
        ('comment','exclusive'),
        ('string','exclusive'),
    )

    escape_char = {
       'b'  : '\\x0b',
       't'  : '\\x09',
       'n'  : '\\x0a',
       'r'  : '\\x0d',
       '"'  : '\\x22',
       '\\' : '\\x5c'
    }

    keywords = {
        'and' : 'and',
        'extends' : 'extends',
        'isnull' : 'isnull',
        'then' : 'then',
        'bool' : 'bool',
        'false' : 'false',
        'let' : 'let',
        'true' : 'true',
        'class' : 'class',
        'if' : 'if',
        'new' : 'new',
        'unit' : 'unit',
        'do' : 'do',
        'in' : 'in',
        'not' : 'not',
        'while' : 'while',
        'else' : 'else',
        'int32' : 'int32',
        'string' : 'string'
    }

    operators = {
        'lbrace',
        'rbrace',
        'lpar',
        'rpar',
        'colon',
        'semicolon',
        'comma',
        'plus',
        'minus',
        'times',
        'div',
        'pow',
        'dot',
        'equal',
        'lower',
        'lower_equal',
        'assign'
    }

    tokens = [
        'integer_literal',
        'type_identifier',
        'object_identifier',
        'string_literal',
        'eof'
    ] + list(keywords.values()) + list(operators)

    # Operator specifications
    t_lbrace = r'{'
    t_rbrace = r'}'
    t_lpar = r'\('
    t_rpar = r'\)'
    t_colon = r':'
    t_semicolon = r';'
    t_comma = r','
    t_plus = r'\+'
    t_minus = r'-'
    t_times = r'\*'
    t_div = r'/'
    t_pow = r'\^'
    t_dot = r'\.'
    t_equal = r'\='
    t_lower = r'\<'
    t_lower_equal = r'\<\='
    t_assign = r'\<-'

    # Regular expressions
    lowercase   = r'[a-z]'
    uppercase   = r'[A-Z]'
    bin_digit   = r'[0-1]'
    digit       = r'[0-9]'
    hex_digit   = r'[0-9A-Fa-f]'
    letter       = r'[a-zA-Z]'
    alphanum    = r'[a-zA-Z0-9]'


    def __init__(self):
        self.last_lex_pos=-1
        self.comment_level = 0
        self.string = ''
        self.string_lexpos = 0
        self.string_lineno = 0
        self.string_column = 0
        self.lexer = lex.lex(module=self)

    def tokenize(self, text):
        tokens = []
        errors = []
        self.lexer.input(text)
        while True:
            try:
                tok = self.lexer.token()
                if not tok: break
                if not hasattr(tok, 'column'):
                    tok.column = self.find_column(tok)
                tokens.append(tok)
            except LexicalError as le:
                errors.append(le)
                print("shit")
        return tokens, errors

    def find_column(self, token):
        return token.lexpos - self.last_lex_pos

    #Regular expression function rules tokens
    #WARNING All tokens defined by functions are added in the same order as
    #they appear in the lexer file.
    #So longer expression first !

    @TOKEN(uppercase + r'(' + letter + r'|' + digit + r'| _ )*')
    def t_type_identifier(self, t):
        t.type = 'type_identifier'
        return t

    @TOKEN(lowercase + r'(' + letter + r'|' + digit + r'| _ )*')
    def t_object_identifier(self, t):
        t.type = self.keywords.get(t.value,'object_identifier')
        return t

### COMMENTS
    @TOKEN(r'//.*')
    def t_single_line_comment(self, t):
        pass

    @TOKEN(r'\(\*')
    def t_open_comment(self, t):
        self.comment_level = 1
        t.lexer.begin('comment')

    @TOKEN(r'\(\*')
    def t_comment_open_nested(self, t):
        self.comment_level += 1

    @TOKEN(r'\*\)')
    def t_comment_close(self, t):
        self.comment_level -= 1
        if self.comment_level < 1:
            t.lexer.begin('INITIAL')

    @TOKEN(r'.')
    def t_comment_any(self, t):
        pass

    @TOKEN(r'\*\)')
    def t_close_comment_error(self, t):
        raise LexicalError(t.lineno, self.find_column(t),
            "Invalid integer literal")


### STRINGS
    @TOKEN(r'"')
    def t_open_string(self, t):
        self.string_lexpos = t.lexpos
        self.string_lineno = t.lineno
        self.string_column = self.find_column(t)
        t.lexer.begin('string')

    @TOKEN(r'"')
    def t_string_close(self, t):
        t.type = 'string_literal'
        t.value = self.string
        t.lexpos = self.string_lexpos
        t.lineno = self.string_lineno
        t.column = self.string_column
        t.lexer.begin('INITIAL')
        return t

    @TOKEN(r'\\[btnr\\"]')
    def t_string_escape_char(self, t):
        self.string += self.escape_char[t.value[1]]

    @TOKEN(r'\\\n\ *')
    def t_string_break(self, t):
        self.last_lex_pos = t.lexpos + 1
        t.lexer.lineno += 1

    @TOKEN(r'\\x' + hex_digit + hex_digit)
    def t_string_hex(self, t):
        self.string += t.value

    @TOKEN(r'.')
    def t_string_any(self, t):
        if t.value == '\\':
            raise LexicalError(t.lineno, self.find_column(t),
                "Invalid character in string literal")
        elif t.value == '\0':
            raise LexicalError(t.lineno, self.find_column(t),
                "Invalid character in string literal")
        elif ord(t.value) < 32 or ord(t.value) > 126:
            self.string += "\\x" + t.value.encode("hex")
        else:
            self.string += t.value


### INTEGER
    @TOKEN(r'0x' + alphanum + r'*')
    def t_hex_integer_literal(self, t):
        t.type = 'integer_literal'
        try:
            t.value = int(t.value[2:], 16)
        except ValueError:
            raise LexicalError(t.lineno, self.find_column(t),
                "Invalid integer literal")
        return t

    # @TOKEN(r'0b' + alphanum + r'*')
    # def t_bin_integer_literal(self, t):
    #     t.type = 'integer_literal'
    #     try:
    #         t.value = int(t.value[2:], 2)
    #     except ValueError:
    #         raise LexicalError(t.lineno, self.find_column(t),
    #             "Invalid integer literal")
    #     return t

    @TOKEN(digit + r'+')
    def t_integer_literal(self, t):
        t.value = int(t.value)
        return t


### LINE FEED
    def t_newline(self, t):
        r'\n'
        self.last_lex_pos = t.lexpos
        t.lexer.lineno += 1

    def t_string_newline(self, t):
        r'\n'
        self.last_lex_pos = t.lexpos
        t.lexer.lineno += 1
        # raise error

    def t_comment_newline(self, t):
        r'\n'
        self.last_lex_pos = t.lexpos
        t.lexer.lineno += 1

### EOF
    def t_eof(self, t):
        return None

    def t_string_eof(self, t):
        raise LexicalError(self.string_lineno, self.string_column,
            "EOF reached in string literal")

    def t_comment_eof(self, t):
        raise LexicalError(0, 0,
            "EOF reached in comment")

### IGNORED CHARS
    t_ignore  = ' \t\r\f'
    t_comment_ignore = ''
    t_string_ignore = ''


### ERROR RULES
    def t_error(self, t):
        t.lexer.skip(1)
        raise LexicalError(t.lineno, self.find_column(t), "Invalid character")

    def t_comment_error(self, t):
        return self.t_error(t)

    def t_string_error(self, t):
        return self.t_error(t)
