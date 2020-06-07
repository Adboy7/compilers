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
# __author__  = "Adrien and Kevin"
# __version__ = '2.0'
__author__  = "Adrien"
__version__ = '3.0'


class Node:
  def __init__(self, lineno, column):
    self.line = lineno
    self.column = column


class Program(Node):
  def __init__(self, list_class=[]):
    self.list_class = list_class

  def add(self, cl):
    self.list_class.append(cl)

  def __str__(self):
    if(isinstance(self.list_class, dict)):
      list_without_object=self.list_class.copy()
      del list_without_object['Object']
      return f"[" + ", ".join([str(x) for key,x in list_without_object.items()]) + "]"
    
    else:
      return f"[" + ", ".join([str(x) for x in self.list_class]) + "]"


class Class(Node):
  def __init__(self, name, fields, methods, lineno, column, parent="Object", parent_lineno=None, parent_column=None):
    self.name = name
    self.fields = fields
    self.methods = methods
    self.parent = parent
    self.lineno= lineno
    self.column= column
    self.parent_lineno = parent_lineno
    self.parent_column = parent_column
    self.inhe_fields=None
    self.inhe_methods=None
    self.all_parents=[]
   
  def __str__(self):
    if isinstance(self.fields, dict) and isinstance(self.methods, dict):
      return f"Class({self.name}, " \
           f"{self.parent}, " \
           f"[{', '.join([str(x) for key,x in self.fields.items()])}], " \
           f"[{', '.join([str(x) for key,x in self.methods.items()])}])"
    else:
      return f"Class({self.name}, " \
            f"{self.parent}, " \
            f"[{', '.join([str(x) for x in self.fields])}], " \
            f"[{', '.join([str(x) for x in self.methods])}])"


class Field(Node):
  def __init__(self, name, type, lineno, column, init_expr=None):
    self.name = name
    self.type = type
    self.init_expr = init_expr
    self.lineno = lineno
    self.column = column
    
  
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
  def __init__(self, name, formals, ret_type, lineno, column, block):
    self.name = name
    self.formals = formals
    self.ret_type = ret_type
    self.block = block
    self.lineno = lineno
    self.column = column
    
  def __str__(self):
    if isinstance(self.formals,dict):
      return f"Method({self.name}, " \
           f"[{', '.join([str(x) for key,x in self.formals.items()])}], " \
           f"{self.ret_type}, " \
           f"{self.block})"
    else:
      return f"Method({self.name}, " \
            f"[{', '.join([str(x) for x in self.formals])}], " \
            f"{self.ret_type}, " \
            f"{self.block})"



class Formal(Node):
  def __init__(self, name, type, lineno, column):
    self.name = name
    self.type = type
    self.lineno = lineno
    self.column = column
    
  
  def __str__(self):
    return f"{self.name} : {self.type}"


class If(Node):
  def __init__(self, cond_expr, then_expr, lineno, column, else_expr=None):
    self.cond_expr = cond_expr
    self.then_expr = then_expr
    self.else_expr = else_expr
    self.lineno = lineno
    self.column = column
    
    

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
  def __init__(self, cond_expr, body_expr, lineno, column):
    self.cond_expr = cond_expr
    self.body_expr = body_expr
    self.lineno = lineno
    self.column = column
    
    
    

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

class Local_variable(Node):
  def __init__(self, name, type, init_expr, lineno, column):
    self.name = name
    self.type = type
    self.init_expr = init_expr
    self.lineno = lineno
    self.column = column

  def __str__(self):
    return f"{self.name}, "\
           f"{self.type} " \
           f"{', ' + str(self.init_expr) if self.init_expr else ''} " 
    
class Let(Node):
  def __init__(self, name, type, scope_expr, lineno, column,lineno_lv,column_lv,init_expr=None):
    self.local_var= Local_variable(name,type,init_expr,lineno_lv,column_lv)
    self.scope_expr = scope_expr
    self.lineno = lineno
    self.column = column

  def __str__(self):
    if isinstance(self.scope_expr, list) and len(self.scope_expr) > 1:
      scope_expr = f"[{', '.join([str(x) for x in self.scope_expr])}]"
    elif isinstance(self.scope_expr, list) and len(self.scope_expr):
      scope_expr = str(self.scope_expr[0])
    else:
      scope_expr = self.scope_expr
    return f"Let({self.local_var}, "\
           f"{scope_expr})"


class Assign(Node):
  def __init__(self, name, expr,lineno,column):
    if isinstance(name, str):
      self.id = Object_identifier(name,lineno,column)
    else:
      self.id = name

    self.expr = expr
    self.lineno = lineno
    self.column = column
  def __str__(self):
    return f"Assign({self.id.name}, {self.expr})"


class UnOp(Node):
  def __init__(self, op, expr,lineno,column):
    self.op = op
    self.expr = expr
    self.lineno = lineno
    self.column = column

  def __str__(self):
    return f"UnOp({self.op}, {self.expr})"


class BinOp(Node):
  def __init__(self, op, left_expr, right_expr,lineno,column):
    self.op = op
    self.left_expr = left_expr
    self.right_expr = right_expr
    self.lineno = lineno
    self.column = column

  def __str__(self):
    return f"BinOp({self.op}, {self.left_expr}, {self.right_expr})"


class Call(Node):
  def __init__(self, method_name, lineno, column ,arg=[], obj_expr="self"):
    self.obj_expr = obj_expr
    self.method_name = method_name
    self.arg = arg
    self.lineno= lineno
    self.column= column

  def __str__(self):
    if isinstance(self.arg, list):
      arg = f"[{', '.join([str(x) for x in self.arg])}]"
    else:
      arg = f"[{self.arg}]"
    return f"Call({self.obj_expr}, " \
           f"{self.method_name}, " \
           f"{arg})"


class New(Node):
  def __init__(self, type_name):
    self.type_name = type_name

  def __str__(self):
    return f"New({self.type_name})"

class Literal(Node):
  def __init__(self, literal,lineno, column):
    self.literal = literal
    self.lineno = lineno
    self.column = column

  def __str__(self):
    return str(self.literal)

class Object_identifier(Node):
  def __init__(self, name, lineno, column):
    self.name = name
    self.lineno = lineno
    self.column = column

  def __str__(self):
    return self.name

class Block(Node):
  def __init__(self, block, lineno, column):
    self.block = block
    self.lineno = lineno
    self.column = column

  def __str__(self):
    if isinstance(self.block, list) and len(self.block) > 1:
      return f"[{', '.join([str(x) for x in self.block])}]"
    elif isinstance(self.block, list) and len(self.block):
      return str(self.block[0])
    else:
      return self.block
