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

  def check_redefine(self):
    # seule la première classe du fichier est considérée comme définie, les redéfinitions ne sont pas enregistrées
    ''' records defined classes and finds duplicates '''
    self.program.classes_table_pointer = {object_class.name: object_class}
    for c in self.program.list_class:
      if c.name in self.program.classes_table_pointer:
        self.errors.append(SemError(f"redefinition of class {c.name}", line=1, column=1))
      else:
        self.program.classes_table_pointer[c.name] = c

  def check_inheritance(self):
    '''checks for cycles and undefined extending class'''
    # si on envoie TOUTES les classes du prog il peut y avoir une erreur de cycle pour une classe redéfinie
    # peut etre mieux de n'envoyer que les classes_table_pointer?

    # if parent is not defined then error
    # ne doit pas etre dans la boucle qui suit sinon elle sera notifiée plusieurs fois
    for c in self.program.list_class:
       if c.parent not in self.program.classes_table_pointer:
          self.errors.append(SemError(f"class {c.parent} not defined", line=1, column=1))
          # here we fool the class, extending Object class for no further error
          c.parent = object_class.name
    
    # classes we know correct
    class_checked = []

    # for each class in file, let's browse their inheritance to find cycles
    for c in self.program.list_class:
      child = c
      parent = self.program.classes_table_pointer[child.parent]
      # records pointer to parent class
      c.parent_pointer = parent
      already_seen = [child.name]

      while True:
        # if parent is ok then child is ok
        if child.parent in class_checked or child.parent == object_class.name:
          for seen in already_seen:
            class_checked.append(seen)
          break
        # if parent is a child's ancestor then error
        elif child.parent in already_seen:
          self.errors.append(SemError(f"class {c.parent} cannot extend child class {c.name}.", line=1, column=1))
          break
        # if parent inherits another class
        else:
          child = parent
          parent = self.program.classes_table_pointer[child.parent]
          already_seen.append(child.name)

  def check_class_body(self):
    for c in self.program.list_class:
      self.check_fields(c)
    for c in self.program.list_class:
      self.check_methods(c)

  def check_fields(self, class_):
    ''' records fields, checks for duplicates and overrides'''

    # already checked
    if hasattr(class_, "fields_table_pointer"):
      return

    # first check parent fields prior to check field redifinition
    if not class_.name == object_class.name and not hasattr(class_.parent_pointer, "fields_table_pointer"):
      self.check_fields(class_.parent_pointer)

    class_.fields_table_pointer = {"self": class_}
    for field in class_.fields:
      field.class_pointer = class_

      # check type
      self.check_expression(field.type)
      # TODO record le type

      # check if field = self
      if field.name == "self":
        self.errors.append(SemError(f"a field named \"self\" is forbidden""", line=1, column=1))
        continue
      # checks for redefinition
      if field.name in class_.parent_pointer.fields_table_pointer:
        self.errors.append(SemError(f"redefinition of field {field.name} from {class_.parent_pointer.name} parent in class {class_.name}", line=1, column=1))
      elif field.name in class_.fields_table_pointer:
        self.errors.append(SemError(f"redefinition of field {field.name} in class {class_.name}", line=1, column=1))
      else:
        class_.fields_table_pointer[field.name] = field

    # records parent fields in child class
    if not class_.name == object_class.name:
      for field_name in class_.parent_pointer.fields_table_pointer:
        if not field_name in class_.fields_table_pointer:
          class_.fields_table_pointer[field_name] = class_.parent_pointer.fields_table_pointer[field_name]
    
    # check init expr
    for field in class_.fields:
      if field.init_expr:
        self.check_expression(field.init_expr)


  def check_methods(self, class_):
    ''' records methods, checks for duplicates and correct overrides '''
    
    # already checked
    if hasattr(class_, "methods_table_pointer"):
      return
    
    # first check parent methods prior to check method inheritance
    if not class_.name == object_class.name and not hasattr(class_.parent_pointer, "methods_table_pointer"):
      self.check_methods(class_.parent_pointer)

    class_.methods_table_pointer = {}

    for method in class_.methods:
      # save class in method
      method.class_pointer = class_

      # check return type
      self.check_expression(method.ret_type)
      # TODO record le type

      # checks for redefinition
      if method.name in class_.methods_table_pointer:
        self.errors.append(SemError(f"redefinition of method {method.name} in class {class_.name}", line=1, column=1))
      else:
        class_.methods_table_pointer[method.name] = method

      # method.formals_table_pointer = {"self": class_}
      method.formals_table_pointer = {}
      method.local_variables_table_pointer={}

      for formal in method.formals:
          # save method in formal
          formal.method = method

          # check formal type
          self.check_expression(formal.type)
          # TODO record le type

          if formal.name == "self":
            self.errors.append(SemError(f"a method named \"self\" is forbidden""", line=1, column=1))
            continue
          # check params redefinition
          if formal.name in method.formals_table_pointer:
            self.errors.append(SemError(f"redefinition of parameter {formal.name} in method {method.name}", line=1, column=1))
          else:
            method.formals_table_pointer[formal.name] = formal
      
      # check return type
      # TODO checker si le ret type correspond

    # check overridden methods
    for method_name in class_.methods_table_pointer:
      if method_name in class_.parent_pointer.methods_table_pointer:
        # method is overridden -> check params
        child_method = class_.methods_table_pointer[method_name]
        parent_method = class_.parent_pointer.methods_table_pointer[method_name]
        if len(child_method.formals_table_pointer) != len(parent_method.formals_table_pointer):
          self.errors.append(SemError(f"overriding method {method_name} with different signature", line=1, column=1))
        if not child_method.ret_type == parent_method.ret_type:
          self.errors.append(SemError(f"overriden method {method_name} returns {child_method.ret_type} but parent's method returns ({parent_method.ret_type})", line=1, column=1))
        
        # TODO check return type
    
    # add inherited methods to table pointer
    if not class_.name == object_class.name:
      for method_name in class_.parent_pointer.methods_table_pointer:
        if not method_name in class_.methods_table_pointer:
          class_.methods_table_pointer[method_name] = class_.parent_pointer.methods_table_pointer[method_name]

    # check expressions in block
    for method in class_.methods:
      for expr in method.block:
        expr.method=method
        print("oui")
        self.check_expression(expr)

  def check_expression(self, expression):

    

    print(type(expression))
    
    if isinstance(expression, (IntegerLiteral,BooleanLiteral,UnitLiteral,StringLiteral)):
      return self.check_expression_literal(expression)
    elif isinstance(expression, BinOp):
      return self.check_expression_binop(expression)
    elif isinstance(expression, UnOp):
      return self.check_expression_unop(expression)
    elif isinstance(expression, While):
      return self.check_expression_while(expression)
    elif isinstance(expression, If):
      return self.check_expression_if(expression)
    elif isinstance(expression, Let):
      return self.check_expression_let(expression)
    elif isinstance(expression, Assign):
      return self.check_expression_assign(expression)
    elif isinstance(expression, Call):
      return self.check_expression_call(expression)
    else:
      print(f"another one {expression}")

  def check_expression_literal(self, expression):
    if isinstance(expression.literal, Literal):
      if expression.literal.literal == "true" or expression.literal.literal == "false":
        print("bool literal")
        return "bool"
    elif isinstance(expression.literal, str):
      if expression.literal == "()":
        print("unit literal")
        return "unit"
      elif expression.literal[0] == '"' and expression.literal[-1]=='"':
        print("string literal")
        return "string"
    elif isinstance(expression.literal, int):
      print("int32 literal")
      if(expression.literal<-2147483648 or expression.literal>2147483647):
        return "error"
      return "int32"

  def check_expression_binop(self, expression):
    print("binop")
    if hasattr(expression, 'method'):
      expression.left_expr.method = expression.method

    if hasattr(expression, 'method'):
      expression.left_expr.method = expression.method
  
    if expression.op == "+" or expression.op == "-"  or expression.op == "*"  or expression.op == "/" or expression.op == "^":
      if self.check_expression(expression.left_expr) != "int32" or self.check_expression(expression.right_expr) != "int32":
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only between type int32', line=1, column=1))
      return "int32"
    if expression.op == "<=" or expression.op == "<":
      if self.check_expression(expression.left_expr) != "int32" or self.check_expression(expression.right_expr) != "int32":
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only between type int32', line=1, column=1))
      return "bool"
    if expression.op == "=":
      if self.check_expression(expression.left_expr) != self.check_expression(expression.right_expr):
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only between expression of the same type', line=1, column=1))
      return "bool"
    if expression.op == "and":
      if self.check_expression(expression.left_expr) != "bool" or self.check_expression(expression.right_expr) != "bool":
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only between type boolean', line=1, column=1))
      return "bool"

  def check_expression_unop(self, expression):
    print("unnop")
    if hasattr(expression, 'method'):
      expression.expr.method = expression.method

    if expression.op == "not":
      if self.check_expression(expression.expr) != "bool":
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only on type boolean', line=1, column=1))
      return "bool"
    if expression.op == "-":
      if self.check_expression(expression.expr) != "int32":
        self.errors.append(SemError(f'operation \"{expression.op}\" can be done only on type int32', line=1, column=1))
      return "int32"

  def check_expression_while(self, expression):
    print("while")
    if hasattr(expression, 'method'):
      expression.cond_expr.method = expression.method
    if self.check_expression(expression.cond_expr) != "bool":
      self.errors.append(SemError(f'the condition of the while is not a boolean', line=1, column=1))
    return "unit"

  def check_expression_if(self, expression):
    print(type(expression.cond_expr))
    if hasattr(expression, 'method'):
      expression.cond_expr.method = expression.method
    if self.check_expression(expression.cond_expr) != "bool":
      self.errors.append(SemError(f'the condition of the if is not a boolean', line=1, column=1))

  def check_expression_let(self, expression):
    print(expression.init_expr)
    print(type(expression.init_expr))
    if(expression.init_expr):
      if hasattr(expression, 'method'):

        expression.init_expr.method = expression.method
      if expression.type != self.check_expression(expression.init_expr):
        self.errors.append(SemError(f'the value of \"{expression.name}\" is not of type \"{expression.type}\"', line=0, column=0))

    if hasattr(expression, 'method'):

      expression.scope_expr.method = expression.method

      previous_local_variable=None
      if expression.name in expression.scope_expr.method.local_variables_table_pointer:
        previous_local_variable=expression.scope_expr.method.local_variables_table_pointer[expression.name]

      expression.scope_expr.method.local_variables_table_pointer[expression.name]=expression
      
      block_type=self.check_expression(expression.scope_expr)
      if previous_local_variable != None: 
        expression.scope_expr.method.local_variables_table_pointer[expression.name]=previous_local_variable
      else:
        del expression.scope_expr.method.local_variables_table_pointer[expression.name]

      return block_type
      
      

  def check_expression_assign(self, expression):
    if expression.name == "self":
      self.errors.append(SemError(f"Cannot assign to self", line=1, column=1))

    if expression.name in expression.method.local_variables_table_pointer:
      if hasattr(expression, 'method'):
        expression.expr.method = expression.method

      if expression.method.local_variables_table_pointer[expression.name].type != self.check_expression(expression.expr):
        self.errors.append(SemError(f"{expression.name} is assign to the wrong type", line=1, column=1))

    elif expression.name in expression.method.class_pointer.fields_table_pointer:
      if hasattr(expression, 'method'):
        print("---")
        print(expression.expr)
        print(type(expression.expr))
        expression.expr.method = expression.method
      if expression.method.class_pointer.fields_table_pointer[expression.name].type != self.check_expression(expression.expr):
        self.errors.append(SemError(f"{expression.name} is assign to the wrong type", line=1, column=1))
      
    else:
      self.errors.append(SemError(f"{expression.name} is unknown", line=1, column=1))


  def check_expression_new(self, expression):
    pass

  def check_expression_call(self, expression):
    print(type(expression.obj_expr))
    print(type(expression.method_name))
    print(expression.expr_list)
    

  def check_main(self):
    main_class = None
    main_method = None
    try:
      main_class = self.program.classes_table_pointer["Main"]
      main_method = main_class.methods_table_pointer["main"]

      if not len(main_method.formals_table_pointer) == 0:
        self.errors.append(SemError(f"main method can't have arguments", line=1, column=1))

      # TODO check return type
    except:
      if main_class == None:
        self.errors.append(SemError(f"program doesn't have a Main class", line=1, column=1))
      elif main_method == None:
        self.errors.append(SemError(f"Main class doesn't have a main method", line=1, column=1))

  def semantic_analysis(self, program):
    self.errors = []
    self.program = program

    # print("check_redefine")
    self.check_redefine()
    # print("check_inheritance")
    self.check_inheritance()
    # print("check_fields & check_methods")
    self.check_class_body()
    self.check_main()
    # print("DONE")
    return self.program, self.errors


