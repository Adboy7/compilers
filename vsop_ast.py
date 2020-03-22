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
  def __init__(self, list_class=[]):
    self.list_class = list_class
  def add(self, cl):
    self.list_class.append(cl)
  def __str__(self):
    return f"[" + ", ".join([str(x) for x in self.list_class]) + "]"


class Class(Node):
  def __init__(self, name, fields, methods, parent="Object"):
    self.name = name
    self.fields = fields
    self.methods = methods
    self.parent = parent

  def __str__(self):
    return f"Class({self.name}, " \
           f"{self.parent}, " \
           f"[{', '.join([str(x) for x in self.fields])}], " \
           f"[{', '.join([str(x) for x in self.methods])}])"

class Field(Node):
  def __init__(self, name, type, init_expr=None):
    self.name = name
    self.type = type
    self.init_expr = init_expr
  
  def __str__(self):
    return f"Field({self.name}, {self.type})"


class Method(Node):
  def __init__(self, name, formals, ret_type, block=[]):
    self.name = name
    self.formals = formals
    self.ret_type = ret_type
    self.block = block

  def __str__(self):
    return f"Method({self.name}, " \
           f"[{', '.join([str(x) for x in self.formals])}], " \
           f"{self.ret_type}, " \
           f"[{', '.join([str(x) for x in self.block])}])"


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
  
  def __str__(self):
    return f"{self.name}:{self.type}"

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

  def __str__(self):
    return f"Let({self.name}, " \
           f"{self.type}{', ' + str(self.init_expr) if self.init_expr else ''}, " \
           f"{self.scope_expr})"


class Assign(Node):
  def __init__(self, name, expr):
    self.name = name
    self.expr = expr
  
  def __str__(self):
    return f"Assign({self.name}, {self.expr})"

class UnOp(Node):
  def __init__(self, op, expr):
    self.op = op
    self.expr = expr

class BinOp(Node):
  def __init__(self, op, left_expr, right_expr):
    self.op = op
    self.left_expr = left_expr
    self.right_expr = right_expr

  def __str__(self):
    return f"BinOp({self.op}, {self.left_expr}, {self.right_expr})"

class Call(Node):
  def __init__(self, method_name, expr_list=[], obj_expr="self"):
    self.obj_expr = obj_expr
    self.method_name = method_name
    self.expr_list = expr_list

  def __str__(self):
    return f"Call({self.obj_expr}, {self.method_name})"

class New(Node):
  def __init__(self, type_name):
    self.type_name = type_name

  def __str__(self):
    return f"New({self.type_name})"

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

class Block(Node):
  def __init__(self):
    self.expr = []
