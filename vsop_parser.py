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

  def p_formals(self,p):
    '''formals : formal
               | formals comma formal
               | empty'''
    print("shit")

  def p_formal(self,p):
    '''formal : object_identifier colon type_identifier'''

  def p_block(self,p):
    '''block : rbrace expression semicolon expression '''
  
  def p_expression(self, p):
      '''expression : if expression then expression
                    | if expression then expression else expression
                    | while expression do expression
                    | let object_identifier colon type_identifier in expression
                    | let object_identifier colon type_identifier assign expression in expression
                    | object_identifier assign expression
                    | not expression
                    | expression and expression
                    | expression equal expression
                    | expression lower_equal expression
                    | expression lower expression
                    | expression plus expression
                    | expression minus expression
                    | expression times expression
                    | expression div expression
                    | expression pow expression
                    | minus expression
                    | isnull expression
                    | object_identifier lpar args rpar
                    | new type_identifier
                    | object_identifier
                    | literal 
                    | lpar rpar
                    | lpar expression rpar
                    | block'''
      p[0]=p[1]
      for i in range(2,len(p)):
        if(p[i]):
          p[0]+=p[i]
      print("express")

  def p_args(self,p):
      '''args : expression 
              | args comma expression
              | empty'''

      print("args")
      p[0]=p[1]
      for i in range(2,len(p)):
        p[0]+=p[i]
 

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
    pass

### ERROR HANDLING
  def p_error(self, p):
    pass


### MAIN
if __name__ == "__main__":
  import sys
  text = 'as(a,a)'
  
  #lexer = VsopLexer()
  #tokens,errors = lexer.tokenize(text)
  #print(tokens)
  parser = VsopParser()
  result = parser.parse(text)
  print("Result :",result)
