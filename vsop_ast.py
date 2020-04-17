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
# May seem messy, but we were fed up of formatting... 
# so almost all nodes have the same format rule
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

class Node:
  # TODO ajouter position au parse
  def __init__(self, line, column):
    self.line = line
    self.column = column


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
    if isinstance(self.init_expr, list) and len(self.init_expr) > 1:
      init_expr = f"[{', '.join([str(x) for x in self.init_expr])}]"
    elif isinstance(self.init_expr, list) and len(self.init_expr):
      init_expr = str(self.init_expr[0])
    else:
      init_expr = self.init_expr
    return f"Field({self.name}, " \
           f"{self.type}" \
           f"{', ' + str(init_expr) if init_expr else ''})"


class Method(Node):
  def __init__(self, name, formals, ret_type, block=[]):
    self.name = name
    self.formals = formals
    self.ret_type = ret_type
    self.block = block

  def __str__(self):
    if isinstance(self.block, list) and len(self.block) > 1:
      block = f"[{', '.join([str(x) for x in self.block])}]"
    elif isinstance(self.block, list) and len(self.block):
      block = str(self.block[0])
    else:
      block = self.block
    return f"Method({self.name}, " \
           f"[{', '.join([str(x) for x in self.formals])}], " \
           f"{self.ret_type}, " \
           f"{block})"


# Useless
class Type(Node):
  def __init__(self, type):
    self.type = type

  def __str__(self):
    return f"{self.type}"


class Formal(Node):
  def __init__(self, name, type):
    self.name = name
    self.type = type
  
  def __str__(self):
    return f"{self.name} : {self.type}"


class If(Node):
  def __init__(self, cond_expr, then_expr, else_expr=None):
    self.cond_expr = cond_expr
    self.then_expr = then_expr
    self.else_expr = else_expr

  def __str__(self):
    if isinstance(self.cond_expr, list) and len(self.cond_expr) > 1:
      cond_expr = f"[{', '.join([str(x) for x in self.cond_expr])}]"
    elif isinstance(self.cond_expr, list) and len(self.cond_expr):
      cond_expr = str(self.cond_expr[0])
    else:
      cond_expr = self.cond_expr

    if isinstance(self.then_expr, list) and len(self.then_expr) > 1:
      then_expr = f"[{', '.join([str(x) for x in self.then_expr])}]"
    elif isinstance(self.then_expr, list) and len(self.then_expr):
      then_expr = str(self.then_expr[0])
    else:
      then_expr = self.then_expr

    if isinstance(self.else_expr, list) and len(self.else_expr) > 1:
      else_expr = f"[{', '.join([str(x) for x in self.else_expr])}]"
    elif isinstance(self.else_expr, list) and len(self.else_expr):
      else_expr = str(self.else_expr[0])
    else:
      else_expr = self.else_expr

    return f"If({cond_expr}, " \
           f"{then_expr}" \
           f"{', ' + str(else_expr) if else_expr else ''})"


class While(Node):
  def __init__(self, cond_expr, body_expr):
    self.cond_expr = cond_expr
    self.body_expr = body_expr

  def __str__(self):
    if isinstance(self.cond_expr, list) and len(self.cond_expr) > 1:
      cond_expr = f"[{', '.join([str(x) for x in self.cond_expr])}]"
    elif isinstance(self.cond_expr, list) and len(self.cond_expr):
      cond_expr = str(self.cond_expr[0])
    else:
      cond_expr = self.cond_expr

    if isinstance(self.body_expr, list) and len(self.body_expr) > 1:
      body_expr = f"[{', '.join([str(x) for x in self.body_expr])}]"
    elif isinstance(self.body_expr, list) and len(self.body_expr):
      body_expr = str(self.body_expr[0])
    else:
      body_expr = self.body_expr

    return f"While({cond_expr}, {body_expr})"


class Let(Node):
  def __init__(self, name, type, scope_expr, init_expr=None):
    self.name = name
    self.type = type
    self.scope_expr = scope_expr
    self.init_expr = init_expr

  def __str__(self):
    if isinstance(self.scope_expr, list) and len(self.scope_expr) > 1:
      scope_expr = f"[{', '.join([str(x) for x in self.scope_expr])}]"
    elif isinstance(self.scope_expr, list) and len(self.scope_expr):
      scope_expr = str(self.scope_expr[0])
    else:
      scope_expr = self.scope_expr
    return f"Let({self.name}, " \
           f"{self.type}{', ' + str(self.init_expr) if self.init_expr else ''}, " \
           f"{scope_expr})"


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

  def __str__(self):
    return f"UnOp({self.op}, {self.expr})"


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
    if isinstance(self.expr_list, list):
      expr_list = f"[{', '.join([str(x) for x in self.expr_list])}]"
    else:
      expr_list = f"[{self.expr_list}]"
    return f"Call({self.obj_expr}, " \
           f"{self.method_name}, " \
           f"{expr_list})"


class New(Node):
  def __init__(self, type_name):
    self.type_name = type_name

  def __str__(self):
    return f"New({self.type_name})"


class Literal(Node):
  def __init__(self, literal):
    self.literal = literal

  def __str__(self):
    return str(self.literal)
