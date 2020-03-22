# -----------------------------------------------------------------------------
# vsop_lexer.py
#
# VSOP Lexer
# lexer == ply.lex
#
# REF:
#   https://www.dabeaz.com/ply/ply.html#ply_nn5
#   https://github.com/dabeaz/ply/blob/master/ply/lex.py
#   https://www.programcreek.com/python/example/101132/ply.lex.lexer
#
# VERSION:
#   v1.0: original
#   v1.1: fix comment error handling
#   v2.0: simplify code to be handle by the parser
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '2.0'

import ply.lex as lex
from ply.lex import TOKEN

class LexicalError():
  def __init__(self, line, column, description):
    self.line = line
    self.column = column
    self.description = description
  
  def __str__(self):
    return f"{self.line}:{self.column}: lexical error: {self.description}"

class VsopLexer():
  states = (
    ('comment','exclusive'),
    ('string','exclusive'),
  )

  escape_char = {
    'b'  : '\\x08',
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
    self.errors = []
    self.last_lf_lexpos = -1
    self.comment_level = []
    self.string = ''
    self.last_lexpos = 0
    self.last_lineno = 0
    self.last_column = 0
    self.lexer = lex.lex(module=self)
  
  def input(self, text):
    self.lexer.input(text)

  def token(self):
    while True:
      t = self.lexer.token()
      break
    if t and not hasattr(t, 'column'):
        t.column = self.find_column(t)
    return t

  def tokenize(self, text):
    tokens = []
    self.lexer.input(text)
    while True:
      tok = self.token()
      if not tok: break
      tokens.append(tok)
    return tokens, self.errors

  def find_column(self, token):
    return token.lexpos - self.last_lf_lexpos

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
    self.comment_level = [(t.lineno,  self.find_column(t), t.lexpos)]
    # self.last_lexpos = t.lexpos
    # self.last_lineno = t.lineno
    # self.last_column = self.find_column(t)
    t.lexer.begin('comment')

  @TOKEN(r'\(\*')
  def t_comment_open_nested(self, t):
    self.comment_level.append((t.lineno,  self.find_column(t), t.lexpos))

  @TOKEN(r'\*\)')
  def t_comment_close(self, t):
    if len(self.comment_level) > 1:
      del self.comment_level[-1]
    else:
      t.lexer.begin('INITIAL')

  @TOKEN(r'.')
  def t_comment_any(self, t):
    pass

  @TOKEN(r'\*\)')
  def t_close_comment_error(self, t):
    self.errors.append(LexicalError(t.lineno, self.find_column(t),
      "Comment not closed"))


### STRINGS
  @TOKEN(r'"')
  def t_open_string(self, t):
    self.string = '"'
    self.last_lexpos = t.lexpos
    self.last_lineno = t.lineno
    self.last_column = self.find_column(t)
    t.lexer.begin('string')

  @TOKEN(r'"')
  def t_string_close(self, t):
    t.type = 'string_literal'
    self.string += '"'
    t.value = self.string
    t.lexpos = self.last_lexpos
    t.lineno = self.last_lineno
    t.column = self.last_column
    t.lexer.begin('INITIAL')
    return t

  @TOKEN(r'\\[btnr\\"]')
  def t_string_escape_char(self, t):
    self.string += self.escape_char[t.value[1]]

  @TOKEN(r'\\\n\ *')
  def t_string_break(self, t):
    self.last_lf_lexpos = t.lexpos + 1
    t.lexer.lineno += 1

  @TOKEN(r'\\x' + hex_digit + hex_digit)
  def t_string_hex(self, t):
    self.string += t.value

  @TOKEN(r'.')
  def t_string_any(self, t):
    if t.value == '\\':
      self.errors.append(LexicalError(t.lineno, self.find_column(t),
        "Invalid character in string literal"))
    elif t.value == '\0':
      self.errors.append(LexicalError(t.lineno, self.find_column(t),
        "Invalid character in string literal"))
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
      return t
    except ValueError:
      self.errors.append(LexicalError(t.lineno, self.find_column(t),
        "Invalid integer literal"))
    
  # @TOKEN(r'0b' + alphanum + r'*')
  # def t_bin_integer_literal(self, t):
  #   t.type = 'integer_literal'
  #   try:
  #     t.value = int(t.value[2:], 2)
  #     return t
  #   except ValueError:
  #     self.errors.append(LexicalError(t.lineno, self.find_column(t),
  #           "Invalid integer literal"))
  

  @TOKEN(alphanum + r'+')
  def t_integer_literal(self, t):
    t.type = 'integer_literal'
    try:
      t.value = int(t.value)
      return t
    except ValueError:
      self.errors.append(LexicalError(t.lineno, self.find_column(t),
          "Invalid integer literal"))  


### LINE FEED
  def t_newline(self, t):
    r'\n'
    self.last_lf_lexpos = t.lexpos
    t.lexer.lineno += 1

  def t_string_newline(self, t):
    r'\n'
    line = t.lexer.lineno
    column = self.find_column(t)
    self.last_lf_lexpos = t.lexpos
    t.lexer.lineno += 1
    self.errors.append(LexicalError(line, column,
      "Invalid raw line feed in string literal"))

  def t_comment_newline(self, t):
    r'\n'
    self.last_lf_lexpos = t.lexpos
    t.lexer.lineno += 1


### EOF
  def t_eof(self, t):
    return None

  def t_string_eof(self, t):
    self.errors.append(LexicalError(self.last_lineno, self.last_column,
      "EOF reached in string literal"))
    return None

  def t_comment_eof(self, t):
    self.errors.append(LexicalError(self.comment_level[-1][0], self.comment_level[-1][1],
      "EOF reached in comment"))
    return None


### IGNORED CHARS
  t_ignore  = ' \t\r\f'
  t_comment_ignore = ''
  t_string_ignore = ''


### ERROR RULES
  def t_error(self, t):
    t.lexer.skip(1)
    self.errors.append(LexicalError(t.lineno, self.find_column(t), "Invalid character"))

  def t_comment_error(self, t):
    return self.t_error(t)

  def t_string_error(self, t):
    return self.t_error(t)


### MAIN  
if __name__ == "__main__":
  import sys
  text = open(sys.argv[1], 'r').read()
  lexer = VsopLexer()
  toks, errors = lexer.tokenize(text)
  for e in errors:
    print(e)
  for t in toks:
    print(f"{t.lineno},{t.column},{t.type}")
