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
#   https://github.com/andfelzapata/python-ply-mini-java/blob/master/parser.py
#
# VERSION:
#   v1.0: original
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

import ply.lex as lex
import ply.yacc as yacc
from vsop_lexer import *
from vsop_ast import *

class ParseError(Exception):
  def __init__(self, line, column, message, token=None, expected=None):
    self.line = line
    self.column = column
    self.message = message

  def __str__(self):
    return f"{self.line}:{self.column}: syntax error: {self.message}"


class VsopParser:
  precedence = (
    ('right', 'assign'),
    ('left', 'and'),
    ('right', 'not'),
    ('nonassoc', 'equal','lower','lower_equal'),
    ('left', 'plus', 'minus'),
    ('left', 'times', 'div'),
    ('right', 'isnull', 'unary_minus'),
    ('right', 'pow'),
    ('left', 'dot'),
  )

  def __init__(self, debug=False):
    self.tokens = VsopLexer.tokens
    self.lexer = VsopLexer()
    self.parser = yacc.yacc(module=self, debug=debug, errorlog=yacc.NullLogger())   

  def parse(self, text):
    self.errors = []
    result = self.parser.parse(text, lexer=self.lexer)
    return result, self.errors

### GRAMMAR RULES
  def p_program(self, p):
    '''program : class_grammar
               | program class_grammar'''
    if len(p) == 3:
      p[0] = p[1]
      p[0].add(p[2])
    else:
      p[0] = Program([p[1]])

  def p_class_grammar(self, p):
    '''class_grammar : class type_identifier lbrace class_body rbrace
                     | class type_identifier extends type_identifier lbrace class_body rbrace'''
    if len(p) == 8:
      p[0] = Class(p[2], p[6][0], p[6][1], p[4])
    else:
      p[0] = Class(p[2], p[4][0], p[4][1])

  def p_class_body(self, p):
    '''class_body : class_body field
                  | class_body method
                  | '''
    if len(p) == 1:
        p[0] = [[], []]
    else:
      p[0] = p[1]
      if type(p[2]) == Field:
        p[0][0].append(p[2])
      elif type(p[2]) == Method:
        p[0][1].append(p[2])
  
  def p_field(self, p):
    '''field : object_identifier colon type semicolon
             | object_identifier colon type assign expression semicolon'''
    if len(p) == 7:
      p[0] = Field(p[1], p[3], p[5])
    else:
      p[0] = Field(p[1], p[3])

  def p_method(self, p):
    '''method : object_identifier lpar formals rpar colon type block'''
    p[0] = Method(p[1], p[3], p[6], p[7])

  def p_type(self, p):
    '''type : type_identifier
            | int32
            | bool
            | string
            | unit'''
    p[0] = p[1]

  def p_formals(self, p):
    '''formals : formal
               | formals comma formal
               | '''
    if len(p) == 1:
      p[0] = []
    elif len(p) == 4 and p[3]:
      p[0] = p[1] + [p[3]]
    elif p[1]:
      p[0] = [p[1]]
    else:
      p[0] = []

  def p_formal(self, p):
    '''formal : object_identifier colon type'''
    p[0] = Formal(p[1], p[3])

  def p_block(self,p):
    '''block : lbrace expressions rbrace '''
    p[0] = p[2]

  def p_expressions(self, p):
    '''expressions : expression
                   | expressions semicolon expression'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
      p[0] = p[1]
      if p[3]:
        p[0].append(p[3])

  def p_expression_if(self, p):
    '''expression : if expression then expression
                  | if expression then expression else expression'''
    if len(p) == 5:
      p[0] = If(p[2], p[4])
    else:
      p[0] = If(p[2], p[4], p[6])

  def p_expression_while(self, p):
    'expression : while expression do expression'
    p[0] = While(p[2], p[4])

  def p_expression_let(self, p):
    '''expression : let object_identifier colon type in expression
                  | let object_identifier colon type assign expression in expression'''

    if len(p) == 7:
      p[0] = Let(p[2], p[4], p[6])
    else:
      p[0] = Let(p[2], p[4], p[8], p[6])
  
  def p_expression_assign(self, p):
    'expression : object_identifier assign expression'
    p[0] = Assign(p[1], p[3])

  def p_expression_unop(self, p):
    '''expression : not expression
                  | minus expression %prec unary_minus
                  | isnull expression'''
    p[0] = UnOp(p[1], p[2])

  def p_expression_binop(self, p):
    '''expression : expression and expression
            | expression equal expression
            | expression lower_equal expression
            | expression lower expression
            | expression plus expression
            | expression minus expression
            | expression times expression
            | expression div expression
            | expression pow expression'''
    p[0] = BinOp(p[2], p[1], p[3])

  def p_expression_call(self, p):
    '''expression : object_identifier lpar args rpar
                  | expression dot object_identifier lpar args rpar'''
    if len(p) == 5:
      p[0] = Call(p[1], p[3])
    else:
      p[0] = Call(p[3], p[5], p[1])

  def p_args(self,p):
    '''args : expression 
            | args comma expression
            | '''
    if len(p) == 1:
      p[0] = []
    elif len(p) == 2:
      p[0] = [p[1]]
    else:
      p[0] = p[1] + [p[3]]

  def p_expression_new(self, p):
    '''expression : new type_identifier'''
    p[0] = New(p[2])

  def p_literal(self,p):
    '''literal : integer_literal
               | string_literal
               | boolean_literal'''
    p[0] = Literal(p[1])

  def p_boolean_literal(self,p):
    '''boolean_literal : true 
                       | false'''
    p[0] = Literal(p[1])

  def p_expression_unit(self, p):
    '''expression : lpar rpar'''
    p[0] = Literal("()")

  def p_expression_par(self, p):
    '''expression : lpar expression rpar'''
    p[0] = p[2]
  
  def p_expression(self, p):
    '''expression : object_identifier
                  | literal
                  | block'''
    p[0] = p[1]
   
  def p_empty(self, p):
    'empty :'
    pass
  

### ERROR HANDLING
  def p_class_grammar_error(self, p):
    '''class_grammar : class error lbrace class_body rbrace'''
    self.errors.append(ParseError(p.lineno, p.column, "Unexpected class name"))

  def p_field_error_semicolon(self, p):
    '''field : object_identifier colon type error
             | object_identifier colon type assign expression error'''
    self.errors.append(ParseError(p.lineno, p.column, "Missing semicolon"))

  

  def p_error(self, p):
    if not p:
      self.errors.append(ParseError(p.lineno, p.column, "Unexpected EOF"))
    else:
      pass
    # else:
    #   self.errors.append(ParseError(p.lineno, p.column, "Unexpected EOF"))


### MAIN
# python vsop_parser.py test.vsop
if __name__ == "__main__":
  import sys
  text = open(sys.argv[1], 'r').read()
  parser = VsopParser(debug=False)
  result, errors = parser.parse(text)
  print(result)
