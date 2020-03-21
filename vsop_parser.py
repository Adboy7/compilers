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
      '''expression : if expression then expression
                    | object_identifier
                    | literal
                    | object_identifier lpar args rpar'''

      if(len(p)== 5):
        p[0]=p[1]+p[2]+p[3]+p[4]
      else:
        p[0]=p[1]
      print("express")

  def p_args(self,p):
    '''args : expression
            | args comma expression'''

    print("args")
    if(len(p)==4):
      p[0]=p[1]+p[2]+p[3]
      print("yes")

    else:
      p[0]=p[1]
 

  def p_literal(self,p):
    '''literal : integer_literal
               | string_literal
               | boolean_literal'''
    p[0]=p[1]
    print("literal",p[0])

  def p_boolean_literal(self,p):
    '''boolean_literal : true 
                       | false'''
    p[0]=p[1]
    print("bool")
   
  

  

  def p_empty(self, p):
    'empty :'
    print("ok",p)
    pass

### ERROR HANDLING
  def p_error(self, p):
    pass


### MAIN
if __name__ == "__main__":
  import sys
  text = 'az(a,n)'
  
  #lexer = VsopLexer()
  #tokens,errors = lexer.tokenize(text)
  #print(tokens)
  parser = VsopParser()
  result = parser.parse(text)
  print("Result :",result)
