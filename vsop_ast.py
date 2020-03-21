# -----------------------------------------------------------------------------
# vsop_ast.py
#
# VSOP Abstract syntax tree
#
# REF:
#   https://github.com/dabeaz/ply/blob/master/ply/yacc.py
#   https://www.dabeaz.com/ply/ply.html#ply_nn34
#   https://github.com/andfelzapata/python-ply-mini-java/blob/master/ast.py
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

class Node:
  pass

class Program(Node):
  def __init__(self, classes=[]):
    self.classes = classes

class Class(Node):
  def __init__(self, name, fields, methods, parent=None):
    self.name = name
    self.fields = fields
    self.methods = methods
    self.parent = parent

class Field(Node):
  def __init__(self, name, type, init_expr=None):
    self.name = name
    self.type = type
    self.init_expr = init_expr

class Method(Node):
  def __init__(self, name, formals, ret_type, block):
    self.name = name
    self.formals = formals
    self.ret_type = ret_type
    self.block = block

class Type(Node):
  def __init__(self, type):
    self.type = type

# class Int32(Type):
#   pass

# class Bool(Type):
#   pass

# class String(Type):
#   pass

# class Unit(Type):
#   pass

class Formal(Node):
  def __init__(self, name, type):
    self.name = name
    self.type = type

class Block(Node):
  pass

class If(Node):
  def __init__(self, cond_expr, then_expr, else_expr=None):
    self.cond_expr = cond_expr
    self.then_expr = then_expr
    self.else_expr = else_expr

class While(Node):
  def __init__(self, cond_expr, body_expr):
    self.cond_expr = cond_expr
    self.body_expr = body_expr

class Let(Node):
  def __init__(self, name, type, scope_expr, init_expr=None):
    self.name = name
    self.type = type
    self.scope_expr = scope_expr
    self.init_expr = init_expr

class Assign(Node):
  def __init__(self, name, expr):
    self.name = name
    self.expr = expr

class UnOp(Node):
  def __init__(self, op, expr):
    self.op = op
    self.expr = expr

class BinOp(Node):
  def __init__(self, op, left_expr, right_expr):
    self.op = op
    self.left_expr = left_expr
    self.right_expr = right_expr

class Call(Node):
  def __init__(self, obj_expr, method_name, expr_list=[]):
    self.obj_expr = obj_expr
    self.method_name = method_name
    self.expr_list = expr_list

class New(Node):
  def __init__(self, type_name):
    self.type_name = type_name

# expr - literal; ???????????????????

class IntegerLiteral(Node):
  def __init__(self, literal):
    self.literal = literal

class StringLiteral(Node):
  def __init__(self, literal):
    self.literal = literal

class BoolLiteral(Node):
  def __init__(self, literal):
    self.literal = literal

class UnitLiteral(Node):
  pass

# expr = "(" expr ")" ???????????