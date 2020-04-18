# -----------------------------------------------------------------------------
# vsop_sem.py
#
# VSOP semantic analysis
#
# REF:
#
# VERSION:
#   v1.0: original
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

# TODO réfléchir comment ajouter l'annotation
# TODO recup ligne et colonne

from vsop_ast import *

class SemError():
  def __init__(self, message, line=None, column=None):
    self.line = line
    self.column = column
    self.message = message

  def __str__(self):
    if not self.line or not self.column:
      return f"semantic error: {self.message}"
    return f"{self.line}:{self.column}: semantic error: {self.message}"

class VsopSem:
  def __init__(self):
    self.errors = []
    self.program = None

  def check_redefine(self, program):
    # seule la première classe du fichier est considérée comme définie, les redéfinitions ne sont pas enregistrées
    defined_classes = {"Object": None}
    for c in program.list_class:
      if c.name in defined_classes:
        self.errors.append(SemError(f"Class {c.name} already defined", line=0, column=0))
      else:
        defined_classes[c.name] = c
    return defined_classes

  def check_inheritance(self, program):
    # si on envoie TOUTES les classes du prog il peut y avoir une erreur de cycle pour une classe redéfinie
    # peut etre mieux de n'envoyer que les defined_classes?
    class_checked = []
    for c in program.list_class:
      child_name = c.name
      parent_name = c.parent
      already_seen = [child_name]

      while True:
        if parent_name in class_checked or parent_name == "Object":
          for seen in already_seen:
            class_checked.append(seen)
          break
        elif parent_name in already_seen:
          self.errors.append(SemError(f"class {child_name} cannot extend child class {parent_name}.", line=0, column=0))
          break
        if parent_name not in self.defined_classes:
          self.errors.append(SemError(f"class {parent_name} not defined", line=0, column=0))
          break
        else:
          child_name = parent_name
          parent_name = self.defined_classes[parent_name].name
          already_seen.append(child_name)
          

  def check_fields(self, program):
    for c in program.list_class:
      if(c.fields):
        already_seen=[]
        for field in c.fields:
          #check if fiel = self
          if(field.name == 'self'):
            self.errors.append(SemError(f"a field named \"self\" is forbidden""", line=0, column=0))
            break
          #check redefinition of field
          if(field.name in already_seen):
            #NEED COLUMN AND LIE OF FIRST DEFINED
            #is this good ? idk
            self.errors.append(SemError(f"redefinition of field {field.name}, first defined at : """, line=0, column=0))
            break
          already_seen.append(field.name)

          if field.init_expr:
            print(type(field.init_expr))
            self.check_expression(field.init_expr)

           

  def check_methods(self, program):
    is_main_class=False
    is_main_method=False 
    for c in program.list_class:
      if(c.methods):
        
        if(c.name == "Main"):
          is_main_class=True
        
        for method in c.methods:
          if(is_main_class and method.name == "main"):
            is_main_method = True
          
          #check if multiple formals with the same name
          formal_already_seen=[]
          for formal in method.formals:
            if(formal.name in formal_already_seen):
              self.errors.append(SemError(f"the formal name \"{formal.name}\" is used multiple times in the method \"{method.name}\"", line=0, column=0))
              break
            formal_already_seen.append(formal.name)

    #if is_main_method is false then there is not main method in the Main class
    if(not is_main_method):
      self.errors.append(SemError(f"the Main class should have a main method", line=0, column=0))

  def check_type(self,ctype,value):
    if(ctype == "bool"):
      print(type(value))
      if value == "true":
        print("what")
        self.errors.append(SemError(f"error", line=0, column=0))

    if(type == "int32"):
      print(value)
    
  def check_expression(self, express):

    if isinstance(express, Literal):
      
      if isinstance(express.literal, Literal):
        if express.literal.literal == "true" or express.literal.literal == "false":
          print("bool")
          return "bool"

      elif isinstance(express.literal, str):
      
        if express.literal == "()":
          return "unit"
        elif express.literal[0] == '"' and express.literal[-1]=='"':
          return "string"

      elif isinstance(express.literal, int):
        if(express.literal<-2147483648 or express.literal>2147483647):
          return "error"
        return "int32"

      else:
        pass
        #error
    
    if isinstance(express, BinOp):
      if express.op == "+" or express.op == "-"  or express.op == "*"  or express.op == "/" or express.op == "^":
        if self.check_expression(express.left_expr) != "int32" or self.check_expression(express.right_expr) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type int32', line=0, column=0))
        return "int32"
      if express.op == "<=" or express.op == "<":
        if self.check_expression(express.left_expr) != "int32" or self.check_expression(express.right_expr) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type int32', line=0, column=0))
        return "bool"
      if express.op == "=":
        if self.check_expression(express.left_expr) != self.check_expression(express.right_expr):
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between expression of the same type', line=0, column=0))
        return "bool"
      if express.op == "and":
        if self.check_expression(express.left_expr) != "bool" or self.check_expression(express.right_expr) != "bool":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type boolean', line=0, column=0))
        return "bool"

    if isinstance(express, UnOp):
      if express.op == "not":
        if self.check_expression(express.expr) != "bool":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only on type boolean', line=0, column=0))
        return bool
      if express.op == "-":
        if self.check_expression(express.expr) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only on type int32', line=0, column=0))

    if isinstance(express, While):
      if self.check_expression(express.cond_expr) != "bool":
        self.errors.append(SemError(f'the condition of the while is not a boolean', line=0, column=0))
      return "unit"


    if isinstance(express, If):
      print(type(express.cond_expr))
      if self.check_expression(express.cond_expr) != "bool":
        self.errors.append(SemError(f'the condition of the if is not a boolean', line=0, column=0))
      
    if isinstance(express, Let):
      print(express.init_expr)
      print(type(express.init_expr))
      if(express.init_expr):
        if express.type != self.check_expression(express.init_expr):
            self.errors.append(SemError(f'the value of \"{express.name}\" is not of type \"{express.type}\"', line=0, column=0))



  def semantic_analysis(self, program):
    self.errors = []
    self.program = program
    self.defined_classes = {}

    print("check_redefine")
    self.defined_classes = self.check_redefine(self.program)
    print("check_inheritance")
    self.check_inheritance(self.program)
    print("===================")
    print("check_field")
    self.check_fields(self.program)
    print("check method")
    self.check_methods(self.program)

    print("DONE")
    return self.program, self.errors


