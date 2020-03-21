# -----------------------------------------------------------------------------
# vsop_parser.py
#
# VSOP parser
# parser == ply.yacc
#
# REF:
#   https://github.com/dabeaz/ply/blob/master/ply/yacc.py
#   https://www.dabeaz.com/ply/ply.html#ply_nn24
#   http://www.matthieuamiguet.ch/pages/compilateurs
#   https://stackoverflow.com/questions/38262552/how-to-encapsulate-the-lex-and-yacc-of-ply-in-two-seperate-class
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

import ply.lex as lex
import ply.yacc as yacc
from vsop_lexer import *

class ParseError(Exception):
  def __init__(self, line, column, message):
    self.line = line
    self.column = column
    self.message = message


class VsopParser:
  def __init__(self):
    self.tokens = VsopLexer.tokens
    self.lexer = VsopLexer()
    self.parser = yacc.yacc(module=self)
    

  def parse(self, text):
    result = self.parser.parse(text)
    return result

### GRAMMAR RULES
  def p_expression(self, p):
    '''expression : int32
                  | string
                  | type_identifier
                  | object_identifier'''
    print("hello")

  def p_empty(self, p):
    'empty :'
    pass

### ERROR HANDLING
  def p_error(self, p):
    pass


### MAIN
if __name__ == "__main__":
  import sys
  text = open(sys.argv[1], 'r').read()
  parser = VsopParser()
  result = parser.parse(text)
  print(result)
