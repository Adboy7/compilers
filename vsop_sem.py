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
# __author__  = "Adrien and Kevin"
# __version__ = '1.0'

__author__  = "Adrien"
__version__ = '2.0'


from vsop_ast import *
import copy

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

  def semantic_analysis(self, program):
    self.errors = []
    self.program = program
    

    #check_redefine_and_main_function and change list_class to a dic
    self.check_redefine_and_main()

    if(not self.errors):
      #if ok check inheritance loop
      self.check_inheritance()
    if(not self.errors):
      #if ok check if fields and method are ok (not the type) 
      #if sem is ok, transform fields and methods array to dic
      #finnaly add inhe field and inhe methods which are also dic
      self.check_and_handle_inheritance_fields_and_methods_loop()
    if(not self.errors):
      #check type of all and check if express are ok
      self.check_fields_and_methods_type()

    return self.program, self.errors

  # 1PASSE
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
            if len(method.formals) != 0 :
              self.errors.append(SemError(f"main method should not have argument", line=method.lineno, column=method.column))
            if method.ret_type != "int32":
              self.errors.append(SemError(f"main method should have return type int32", line=method.lineno, column=method.column))

    if not is_main_class :
      self.errors.append(SemError(f"Main class is missing", line=1, column=1))
    elif not is_main_method:
      self.errors.append(SemError(f"main method in Main class is missing", line=1, column=1))
    
    self.program.list_class = defined_classes

  def create_object_class(self):
    methods=[]
    methods.append(Method('print', [Formal('s','string',0,0)], 'Object',0,0,Block([],0,0)))
    methods.append(Method('printBool', [Formal('b','bool',0,0)],'Object',0,0,Block([],0,0)))
    methods.append(Method('printInt32', [Formal('i','int32',0,0)],'Object',0,0,Block([],0,0)))
    methods.append(Method('inputLine',[],'string',0,0,Block([],0,0)))
    methods.append(Method('inputBool',[],'bool',0,0,Block([],0,0)))
    methods.append(Method('inputInt32',[],'int32',0,0,Block([],0,0)))
    return Class('Object',None,methods,0,0,None)
  
  #2 PASSE
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


  #3PASSE
  def check_and_handle_inheritance_fields_and_methods_loop(self):
    for key, cl in self.program.list_class.items():
      self.check_and_handle_inheritance_fields_and_methods(cl)
      

  def check_and_handle_inheritance_fields_and_methods(self,cl):
    if cl.parent == None:
      if(cl.inhe_fields==None or cl.inhe_methods == None):
        self.check_fields_and_method(cl)
        #Seems not useful but is used as a flag to not perform check_fields_and_methods twice
        cl.inhe_fields={}
        cl.inhe_methods={}
      return copy.deepcopy(cl.methods),{},["Object"]
    else:
      
      if(cl.inhe_methods == None or cl.inhe_fields == None):
        self.check_fields_and_method(cl) 
        inhe_methods, inhe_fields,cl.all_parents=self.check_and_handle_inheritance_fields_and_methods(self.program.list_class[cl.parent])
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
                
              elif method.ret_type != inhe_methods[method.name].ret_type:
                self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same return type than the parent class method", line=method.lineno, column=method.column))
                
              else:
                for key,formal in inhe_methods[method.name].formals.items():
                  if formal.name not in method.formals:
                    self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same formal(s) than the parent class method", line=method.lineno, column=method.column))
                   
                  elif formal.type != method.formals[formal.name].type:
                    self.errors.append(SemError(f"redefinition of method name \"{method.name}\" of class \"{cl.name}\" must have the same formal(s) than the parent class method", line=method.lineno, column=method.column))
                    
                  #if all ok then keeps tracks of redef method to supress then before sending to the child class prevent 2 same class in inhe_method of child
        cl.inhe_methods=inhe_methods

      
      methods_for_child=cl.inhe_methods.copy()
      #With updaten if there is a redefinition it's the parent method which is given to the child not the redefinition
      methods_for_child.update(cl.methods)

      fields_for_child=cl.inhe_fields.copy()
      
      fields_for_child.update(cl.fields)

      all_parents_for_child = copy.deepcopy(cl.all_parents)
      all_parents_for_child.append(cl.name)
      return methods_for_child, fields_for_child, all_parents_for_child


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



  #4 passe
  def check_fields_and_methods_type(self):
    for key,cl in self.program.list_class.items():
      self.check_field_type(cl)
      if cl.name != "Object":
        self.check_method_type_and_body(cl)

  def check_field_type(self,cl):
    for key,field in cl.fields.items():
    #check if init_expr have the right type
      if field.init_expr:
        express_type=self.check_expression(field.init_expr,cl)
        if isinstance(express_type, str):
          if field.type != express_type:
            self.errors.append(SemError(f"the field {field.name} is assigned to a type {express_type} instead of a type {field.type}", line=field.lineno, column=field.column))
        else:
          if not field.type in express_type:
            self.errors.append(SemError(f"the field {field.name} is not assigned to type {field.type}", line=field.lineno, column=field.column))
  
  def check_method_type_and_body(self,cl):
    for key,method in cl.methods.items():
      body_type = self.check_expression(method.block,cl,method.formals)
      if isinstance(body_type,list):
        if not method.ret_type in body_type:
          self.errors.append(SemError(f"return type of method {method.name} is not the same as the body return type", line=method.lineno, column=method.column))
      elif body_type != method.ret_type:
          self.errors.append(SemError(f"return type of method {method.name} is not the same as the body return type", line=method.lineno, column=method.column))

  def check_expression(self, express, cl, formals={}, local_vars={}):
    # == LITERAL ==
    if isinstance(express, Literal):
      if isinstance(express.literal, Literal):
        if express.literal.literal == "true" or express.literal.literal == "false":
          return "bool"

      elif isinstance(express.literal, str):
        if express.literal == "()":
          return "unit"
        elif express.literal[0] == '"' and express.literal[-1]=='"':
          return "string"

      elif isinstance(express.literal, int):
        if(express.literal<-2147483648 or express.literal>2147483647):
          self.errors.append(SemError(f"literal is too big, int32 should be represent as a 32-bit signed integers", line=express.lineno, column=express.column))
          return "error"
        return "int32"

      else:
        self.errors.append(SemError(f"unknown literal", line=express.lineno, column=express.column))
        return "error"

    # == OBJECT IDENTIFIER ==
    if isinstance(express, Object_identifier):
      var_not_found = True

      #Check if is in local variable
      if local_vars and var_not_found:
        if express.name in local_vars:
          var_not_found=False
          if local_vars[express.name].type == "unit" or local_vars[express.name].type == "bool" or local_vars[express.name].type == "int32" or local_vars[express.name].type == "string":
            return local_vars[express.name].type
          #It's a class type
          else:
            #Possible type for a class type is its class type + parent class type
            possible_class_type=copy.deepcopy(self.program.list_class[local_vars[express.name].type].all_parents)
            possible_class_type.append(local_vars[express.name].type)
            return possible_class_type

      #Check if is in formals
      if formals and var_not_found:
        if express.name in formals:
          var_not_found=False
          if formals[express.name].type == "unit" or formals[express.name].type == "bool" or formals[express.name].type == "int32" or formals[express.name].type == "string":
            return formals[express.name].type
          #It's a class type
          else:
            #Possible type for a class type is its class type + parent class type
            possible_class_type=copy.deepcopy(self.program.list_class[formals[express.name].type].all_parents)
            possible_class_type.append(formals[express.name].type)
            return possible_class_type

      #Check if is in fields
      if cl.fields and var_not_found:
        
        if express.name in cl.fields:
          var_not_found=False
          if cl.fields[express.name].type == "unit" or cl.fields[express.name].type == "bool" or cl.fields[express.name].type == "int32" or cl.fields[express.name].type == "string":
            return cl.fields[express.name].type
          #It's a class type
          else:
            #Possible type for a class type is its class type + parent class type
            possible_class_type=copy.deepcopy(self.program.list_class[cl.fields[express.name].type].all_parents)
            possible_class_type.append(cl.fields[express.name].type)
            return possible_class_type

      #Check if is in inhe fields
      if cl.inhe_fields and var_not_found:
        if express.name in cl.inhe_fields:
          var_not_found=False
          if cl.inhe_fields[express.name].type == "unit" or cl.inhe_fields[express.name].type == "bool" or cl.inhe_fields[express.name].type == "int32" or cl.inhe_fields[express.name].type == "string":
            return cl.inhe_fields[express.name].type
          #It's a class type
          else:
            #Possible type for a class type is its class type + parent class type
            possible_class_type=copy.deepcopy(self.program.list_class[cl.inhe_fields[express.name].type].all_parents)
            possible_class_type.append(cl.inhe_fields[express.name].type)
            return possible_class_type
      
      if var_not_found:
        self.errors.append(SemError(f"{express.name} is not defined", line=express.lineno, column=express.column))
        return "error"

    # == BINOP ==
    if isinstance(express, BinOp):
      if express.op == "+" or express.op == "-"  or express.op == "*"  or express.op == "/" or express.op == "^":
        if self.check_expression(express.left_expr,cl,formals,local_vars) != "int32" or self.check_expression(express.right_expr,cl,formals,local_vars) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type int32', line=express.lineno, column=express.column))
          return "error"
        return "int32"
      if express.op == "<=" or express.op == "<":
        if self.check_expression(express.left_expr,cl,formals,local_vars) != "int32" or self.check_expression(express.right_expr,cl,formals,local_vars) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type int32', line=express.lineno, column=express.column))
          return "error"
        return "bool"
      if express.op == "=":
        left_type = self.check_expression(express.left_expr,cl,formals,local_vars)
        right_type = self.check_expression(express.right_expr,cl,formals,local_vars)
        if isinstance(left_type, list) and isinstance(right_type, list) :
          #both are class type so its ok
          return "bool"
        elif left_type == "error" or right_type == "error" or left_type != right_type: 
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between expression of the same type', line=express.lineno, column=express.column))
          return "error"
        return "bool"
      if express.op == "and":
        if self.check_expression(express.left_expr,cl,formals,local_vars) != "bool" or self.check_expression(express.right_expr,cl,formals,local_vars) != "bool":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only between type boolean', line=express.lineno, column=express.column))
          return "error"
        return "bool"

    # == UNOP ==
    if isinstance(express, UnOp):
      if express.op == "not":
        if self.check_expression(express.expr,cl,formals,local_vars) != "bool":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only on type boolean', line=express.lineno, column=express.column))
          return "error"
        return "bool"
      if express.op == "-":
        if self.check_expression(express.expr,cl,formals,local_vars) != "int32":
          self.errors.append(SemError(f'operation \"{express.op}\" can be done only on type int32', line=express.lineno, column=express.column))
          return "error"
        return "int32"

    # == NEW ==
    if isinstance(express, New):
      possible_class_type=copy.deepcopy(self.program.list_class[express.type_name].all_parents)
      possible_class_type.append(express.type_name)
      return possible_class_type
    # == ASSIGN ==
    if isinstance(express, Assign):
      if express.id.name == "self":
        self.errors.append(SemError(f'cannot assign to self', line=express.lineno, column=express.column))
        return "error"

      id_type = self.check_expression(express.id,cl,formals,local_vars)
      if isinstance(id_type, list):
        id_type=id_type[-1]
      express_type = self.check_expression(express.expr,cl,formals,local_vars)
      if isinstance(express_type, list):
        if not id_type in express_type:
          self.errors.append(SemError(f'{express.id.name} is not assign to a type {id_type}', line=express.lineno, column=express.column))
          return "error"
        return "unit"
      else:
        if id_type != express_type:
          self.errors.append(SemError(f'{express.id.name} is not assign to a type {id_type}', line=express.lineno, column=express.column))
          return "error"
        return "unit"

    # == CALL ==
    if isinstance(express, Call):
      #SELF
      
      if express.obj_expr == "self" or (isinstance(express.obj_expr, Object_identifier) and express.obj_expr.name == "self"):
        #check if is in its own methods
        if express.method_name in cl.methods:
          if len(express.arg) != len (cl.methods[express.method_name].formals):
            self.errors.append(SemError(f'number of argument does not match', line=express.lineno, column=express.column))
            return "error"
          else:
            #check argument type ok with formal
            i=0
            for key,formal in cl.methods[express.method_name].formals.items():
              arg_type = self.check_expression(express.arg[i],cl,formals,local_vars)
              if isinstance(arg_type, str):
                if arg_type != formal.type:
                  self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                  return "error"
              elif not formal.type in arg_type:
                self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                return "error"
              
              i+=1
            
            if cl.methods[express.method_name].ret_type in self.program.list_class:
              possible_class_type=copy.deepcopy(self.program.list_class[cl.methods[express.method_name].ret_type].all_parents)
              possible_class_type.append(cl.methods[express.method_name].ret_type)
              return possible_class_type
            else:
              return cl.methods[express.method_name].ret_type

        #else check in inhe methods
        elif express.method_name in cl.inhe_methods:
          if len(express.arg) != len (cl.inhe_methods[express.method_name].formals):
            self.errors.append(SemError(f'number of argument does not match', line=express.lineno, column=express.column))
            return "error"
          else:
            #check argument type ok with formal
            i=0
            for key,formal in cl.inhe_methods[express.method_name].formals.items():
              arg_type = self.check_expression(express.arg[i],cl,formals,local_vars)
              if isinstance(arg_type, str):
                if arg_type != formal.type:
                  self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                  return "error"
              elif not formal.type in arg_type:
                self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                return "error"
              i+=1

            if cl.inhe_methods[express.method_name].ret_type in self.program.list_class:
              possible_class_type=copy.deepcopy(self.program.list_class[cl.inhe_methods[express.method_name].ret_type].all_parents)
              possible_class_type.append(cl.inhe_methods[express.method_name].ret_type)
              return possible_class_type
            else:
              return cl.inhe_methods[express.method_name].ret_type
        else:
          self.errors.append(SemError(f'Unknown method', line=express.lineno, column=express.column))
          return "error"
      
      #NOT SELF
      else:
        
        object_type=self.check_expression(express.obj_expr,cl,formals,local_vars)
        if not isinstance(object_type, list):
          self.errors.append(SemError(f'dispatch is not use on a class object', line=express.lineno, column=express.column))
          return "error"
        else:
          #the last cell of the tab is the type of the object, the rest is its parent
          object_type=object_type[-1]
          #check in its methods
          if express.method_name in self.program.list_class[object_type].methods:
            if len(express.arg) != len (self.program.list_class[object_type].methods[express.method_name].formals):
              self.errors.append(SemError(f'number of argument does not match', line=express.lineno, column=express.column))
              return "error"
            else:
              #check argument type ok with formal
              i=0
              for key,formal in self.program.list_class[object_type].methods[express.method_name].formals.items():
                arg_type = self.check_expression(express.arg[i],cl,formals,local_vars)
                if isinstance(arg_type, str):
                  if arg_type != formal.type:
                    self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                    return "error"
                elif not formal.type in arg_type:
                  self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                  return "error"
                
                i+=1
              
              if self.program.list_class[object_type].methods[express.method_name].ret_type in self.program.list_class:
                possible_class_type=copy.deepcopy(self.program.list_class[self.program.list_class[object_type].methods[express.method_name].ret_type].all_parents)
                possible_class_type.append(self.program.list_class[object_type].methods[express.method_name].ret_type)
                return possible_class_type
              else:
                return self.program.list_class[object_type].methods[express.method_name].ret_type
          
          #check in its inhe methods
          elif express.method_name in self.program.list_class[object_type].inhe_methods:
            if len(express.arg) != len (self.program.list_class[object_type].inhe_methods[express.method_name].formals):
              self.errors.append(SemError(f'number of argument does not match', line=express.lineno, column=express.column))
              return "error"
            else:
              #check argument type ok with formal
              i=0
              for key,formal in self.program.list_class[object_type].inhe_methods[express.method_name].formals.items():
                arg_type = self.check_expression(express.arg[i],cl,formals,local_vars)
                if isinstance(arg_type, str):
                  if arg_type != formal.type:
                    self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                    return "error"
                elif not formal.type in arg_type:
                  self.errors.append(SemError(f'{express.arg[i]} type does not match', line=express.lineno, column=express.column))
                  return "error"
                
                i+=1
              
              if self.program.list_class[object_type].inhe_methods[express.method_name].ret_type in self.program.list_class:
                possible_class_type=copy.deepcopy(self.program.list_class[self.program.list_class[object_type].inhe_methods[express.method_name].ret_type].all_parents)
                possible_class_type.append(self.program.list_class[object_type].inhe_methods[express.method_name].ret_type)
                return possible_class_type
              else:
                return self.program.list_class[object_type].inhe_methods[express.method_name].ret_type
          else:
            self.errors.append(SemError(f'Unknown method', line=express.lineno, column=express.column))
            return "error"
    
    # == BLOCK ==
    if isinstance(express, Block):
      for expr in express.block:
        if expr == express.block[-1]:
          return self.check_expression(expr,cl,formals,local_vars)
        self.check_expression(expr,cl,formals,local_vars)
        

    # == WHILE ==
    if isinstance(express, While):
      if self.check_expression(express.cond_expr,cl,formals,local_vars) != "bool":
        self.errors.append(SemError(f'the condition of the while is not a boolean', line=express.lineno, column=express.lineno))
        return "error"
      self.check_expression(express.body_expr,cl,formals,local_vars)
      return "unit"

    # == IF ==
    if isinstance(express, If):
      if self.check_expression(express.cond_expr,cl,formals,local_vars) != "bool":
        self.errors.append(SemError(f'the condition of the if is not a boolean', line=express.lineno, column=express.lineno))
        return "error"
      if not express.else_expr :
        return self.check_expression(express.then_expr,cl,formals,local_vars)
      else:
        else_type=self.check_expression(express.else_expr,cl,formals,local_vars)
        then_type=self.check_expression(express.then_expr,cl,formals,local_vars)

        #if both are class type
        if isinstance(else_type, list) and isinstance(then_type, list):
          #if its a list, its the list of the type class and all its parents in reverse order so
          #[grand-father,father,class type] so to find first common ancestor you need to reversed the tab
          #note that object is always in the first cell so the if in the loop is always satisfied 
          else_type.reverse()
          for else_class_type in else_type:
            if else_class_type in then_type:
              #return the class type plus the parents
              possible_class_type = copy.deepcopy(self.program.list_class[else_class_type].all_parents)
              possible_class_type.append(else_class_type)
              return possible_class_type
          #this error should never happen but in case of error in the compilers   
          self.errors.append(SemError(f'Unknown problem with then and else, both are class but does not have common ancestor', line=express.lineno, column=express.lineno))
          return "error"

        elif else_type == "unit" or then_type == "unit":
          return "unit"
        
        elif else_type != "error" and then_type != "error" and else_type == then_type:
          return then_type
        else:
          self.errors.append(SemError(f'the type of the then expression and else expression should agree or one of them be unit', line=express.lineno, column=express.lineno))
          return "error"
    
    # == LET ==
    if isinstance(express, Let):
      #check local var != self
      if express.local_var.name == 'self':
        self.errors.append(SemError(f"a local variable named \"self\" is forbidden", line=express.lineno, column=express.column))
        return "error"
      #check local var type
      if express.local_var.type == "unit" or express.local_var.type == "bool" or express.local_var.type == "int32" or express.local_var.type == "string":
        #check init if exist
        if express.local_var.init_expr:
          if express.local_var.type != self.check_expression(express.local_var.init_expr,cl,formals,local_vars):
              self.errors.append(SemError(f'the value of \"{express.local_var.name}\" is not of type \"{express.local_var.type}\"', line=express.local_var.lineno, column=express.local_var.column))
              return "error"
        #All ok check the body
        new_local_vars=copy.deepcopy(local_vars)
        new_local_vars[express.local_var.name]=express.local_var
        return self.check_expression(express.scope_expr,cl,formals,new_local_vars)

      elif express.local_var.type in self.program.list_class:
        #check ini if exist
        if express.local_var.init_expr:
          init_expr_type = self.check_expression(express.init_expr,cl,formals,local_vars)
          if isinstance(init_expr_type, str) or not express.local_var.type in init_expr_type:
            self.errors.append(SemError(f'the initial value of \"{express.local_var.name}\" is not of type \"{express.local_var.type}\"', line=express.local_var.lineno, column=express.local_var.column))
            return "error"
        #All ok check the body
        new_local_vars=copy.deepcopy(local_vars)
        new_local_vars[express.local_vars.name]=express.local_var
        return self.check_expression(express.scope_expr,cl,formals,new_local_vars)

      else:
        self.errors.append(SemError(f"the type of local variable \"{express.local_var.name}\" is {express.local_var.type} which does not exist. ", line=express.local_var.lineno, column=express.local_var.column))
        return "error"
