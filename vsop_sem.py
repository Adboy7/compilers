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
__version__ = '2.0'

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


  def check_redefine_and_main(self):
    # check redefine
    cl_object = self.create_object_class()
    defined_classes = {"Object": cl_object}
    is_main_class=False
    is_main_method=False 
    for cl in self.program.list_class:
      if cl.name in defined_classes:
        self.errors.append(SemError(f"Class {cl.name} already defined", line=cl.lineno, column=cl.column))
      else:
        defined_classes[cl.name] = cl
      # check main
      if cl.name == "Main":
        is_main_class = True
        for method in cl.methods:
          if method.name == "main":
            is_main_method = True
    if not is_main_class :
      self.errors.append(SemError(f"Main class is missing", line=1, column=1))
    elif not is_main_method:
      self.errors.append(SemError(f"main method in Main class is missing", line=1, column=1))
    
    return defined_classes

  def check_inheritance(self):
    
    class_checked = []
    for key,cl in self.program.list_class.items():
      child_name = cl.name
      parent_name = cl.parent
      already_seen = [child_name]

      while True:
        if child_name=="Object":
          break
        if parent_name in class_checked or parent_name == "Object":
          for cl_seen in already_seen:
            class_checked.append(cl_seen)
          break
        elif parent_name in already_seen:
          self.errors.append(SemError(f"class {cl.name} cannot extend child class {cl.parent}, there is a loop.", line=cl.lineno, column=cl.column))
          break
        if parent_name not in self.program.list_class:
          self.errors.append(SemError(f"class {parent_name} not defined", line=cl.parent_lineno, column=cl.parent_column))
          break
        else:
          child_name = parent_name
          parent_name = self.program.list_class[parent_name].parent
          already_seen.append(child_name)


  def create_object_class(self):
    methods=[]
    methods.append(Method('print', [Formal('s','string',0,0)], 'Object',0,0))
    methods.append(Method('printBool', [Formal('b','bool',0,0)],'Object',0,0))
    methods.append(Method('inputLine',[],'string',0,0))
    methods.append(Method('inputBool',[],'bool',0,0))
    methods.append(Method('inputInt32',[],'int32',0,0))
    return Class('Object',None,methods,0,0,None)



  def check_and_handle_inheritance_fields_and_method(self):
    for key, cl in self.program.list_class.items():
      self.check_fields_and_method(cl)
    for key, cl in self.program.list_class.items():
      self.handle_inheritance(cl)
      

  def handle_inheritance(self,cl):
    if cl.parent == None:
      return cl.methods.copy(),{}
    else:
      
      if(cl.inhe_methods == None or cl.inhe_fields == None): 
        inhe_methods, inhe_fields=self.handle_inheritance(self.program.list_class[cl.parent])
        #check field with same name then add inhe fields to the class.
        if(cl.fields):
          for key,field in cl.fields.items():
            if field.name in inhe_fields:
              self.errors.append(SemError(f"field name \"{field.name}\" of class \"{cl.name}\" is already used in one of its parent class ", line=field.lineno, column=field.column))
              del inhe_fields[field.name]
        cl.inhe_fields=inhe_fields

        #check redef method add inhe methods to the class.

        if(cl.methods):
          for key,method in cl.methods.items():
            if method.name in inhe_methods:
              if len(method.formals) != len(inhe_methods[method.name].formals):
                self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same number of formal(s) than the parent class method", line=method.lineno, column=method.column))
                del cl.methods[method.name]
              elif method.ret_type != inhe_methods[method.name].ret_type:
                self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same return type than the parent class method", line=method.lineno, column=method.column))
                del cl.methods[method.name]
              else:
                for formal in inhe_methods[method.name].formals:
                  if formal.name not in method.formals:
                    self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same formal(s) than the parent class method", line=method.lineno, column=method.column))
                    del cl.methods[method.name]
                  elif formal.type != method.formals[formal.name].type:
                    self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same formal(s) than the parent class method", line=method.lineno, column=method.column))
                    del cl.methods[method.name]
                  #if all ok then keeps tracks of redef method to supress then before sending to the child class prevent 2 same class in inhe_method of child
                  else:
                    cl.redef_methods.append(method.name)
        cl.inhe_methods=inhe_methods

      methods_for_child=cl.methods.copy()
      if(cl.redef_methods):
        for redef_method in cl.redef_methods:
          del methods_for_child[redef_method]
      methods_for_child.update(cl.inhe_methods)

      fields_for_child=cl.fields.copy()
      fields_for_child.update(cl.inhe_fields)

      return methods_for_child,fields_for_child


  def check_fields_and_method(self,cl):
      self.check_fields(cl)
      self.check_methods(cl)

  def check_fields(self, cl):
      fields_already_seen={}
      if(cl.fields):
        for field in cl.fields:
          #check if field = self
          if(field.name == 'self'):
            self.errors.append(SemError(f"a field named \"self\" is forbidden", line=field.lineno, column=field.column))
            
          else:
              #check redefinition of field
              if(field.name in fields_already_seen):
                self.errors.append(SemError(f"redefinition of field \"{field.name}\", first defined at {fields_already_seen[field.name].lineno}:{fields_already_seen[field.name].column} """, line=field.lineno, column=field.column))
              else:
                fields_already_seen[field.name] = field

                #check if type is primitive or Class
                if field.type == "unit" or field.type == "bool" or field.type == "int32" or field.type == "string":
                  pass
                elif field.type in self.program.list_class:
                  pass
                else:
                  self.errors.append(SemError(f"the type of field \"{field.name}\" is {field.type} which does not exist. ", line=field.lineno, column=field.column))
      
      #transform into a dico
      cl.fields=fields_already_seen     
      
           
            

          # #check if init_expr have the right type
          # if field.init_expr:
          #   if field.type != self.check_expression(field.init_expr):
          #     self.errors.append(SemError(f"the field {field.name} is assigned to a type {self.check_expression(field.init_expr)} instead of a type {field.type}", line=field.lineno, column=field.column))
          # #if there is no init_expr default-initialized
          # elif field.type == "int32":
          #   field.init_expr = 0
          # elif field.type == "string":
          #   field.init_expr = ""
          # elif field.type == "bool":
          #   field.init_expr = "false"
           

  def check_methods(self, cl):
      method_already_seen={}
      if(cl.methods):
        #check if multiple methods with the same name
        for method in cl.methods:
          if method.name in method_already_seen:
             self.errors.append(SemError(f"the method name \"{method.name}\" is used multiple times in the class \"{cl.name}\"", line=method.lineno, column=method.column))
          else:
            method_already_seen[method.name] = method
            
            formal_already_seen={}
            for formal in method.formals:
              #check if multiple formals with the same name
              if formal.name in formal_already_seen:
                self.errors.append(SemError(f"the formal name \"{formal.name}\"  is used multiple times in the method \"{method.name}\"", line=formal.lineno, column=formal.column))
              else: 
                formal_already_seen[formal.name] = formal

              #check if type is primitive or Class
              if formal.type == "unit" or formal.type == "bool" or formal.type == "int32" or formal.type == "string":
                pass
              elif formal.type in self.program.list_class:
                pass
              else:
                self.errors.append(SemError(f"the type of formal \"{formal.name}\" is {formal.type} which does not exist. ", line=formal.lineno, column=formal.column))
            
            method.formals=formal_already_seen
            if method.ret_type == "unit" or method.ret_type == "bool" or method.ret_type == "int32" or method.ret_type == "string":
              pass
            elif method.ret_type in self.program.list_class:
              pass
            else:
              self.errors.append(SemError(f"the return type of method \"{method.name}\" is {method.ret_type} which does not exist. ", line=method.lineno, column=method.column))
      
      cl.methods=method_already_seen          


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
        return "bool"
      if express.op == "-":
        if self.check_expression(express.expr) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only on type int32', line=0, column=0))
        return "int32"
    if isinstance(express, While):
      if self.check_expression(express.cond_expr) != "bool":
        self.errors.append(SemError(f'the condition of the while is not a boolean', line=0, column=0))
      return "unit"


    if isinstance(express, If):
      print(type(express.cond_expr))
      if self.check_expression(express.cond_expr) != "bool":
        self.errors.append(SemError(f'the condition of the if is not a boolean', line=0, column=0))
      
    if isinstance(express, Let):
      print(type(express.init_expr))
      if(express.init_expr):
        if express.type != self.check_expression(express.init_expr):
            self.errors.append(SemError(f'the value of \"{express.name}\" is not of type \"{express.type}\"', line=0, column=0))



  def semantic_analysis(self, program):
    self.errors = []
    self.program = program
    

    print("check_redefine_and_main")
    program.list_class = self.check_redefine_and_main()
    print("check_inheritance")
    self.check_inheritance()
    print("===================")
    print("check_field")
    self.check_and_handle_inheritance_fields_and_method()
    print(type(self.program.list_class))
    for y,a in self.program.list_class.items():
      print(y,a.inhe_methods)
    print("DONE")
    return self.program, self.errors


