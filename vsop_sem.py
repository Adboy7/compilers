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
    classes_table_pointer = {object_class.name: object_class}
    for c in self.program.list_class:
      if c.name in classes_table_pointer:
        self.errors.append(SemError(f"redefinition of class {c.name}", line=1, column=1))
      else:
        classes_table_pointer[c.name] = c
    self.program.classes_table_pointer = classes_table_pointer

  def check_inheritance(self):
    '''checks for cycles and undefined extending class'''
    # si on envoie TOUTES les classes du prog il peut y avoir une erreur de cycle pour une classe redéfinie
    # peut etre mieux de n'envoyer que les classes_table_pointer?

    # ne doit pas etre dans la boucle qui suit sinon elle sera notifiée plusieurs fois
    # if parent is not defined then error
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
          

  def check_fields(self, class_):
    pass

  def check_methods(self, class_):
    ''' records methods, checks for duplicates and correct overrides '''

    # first check parent methods prior to check method inheritance
    if not hasattr(class_.parent_pointer, "methods_table_pointer"):
      self.check_methods(class_.parent_pointer)

    class_.methods_table_pointer = {}

    
    for method in class_.methods:
      # save class in method
      method.class_pointer = class_

      # checks for redefinition
      if method.name in class_.methods_table_pointer:
        self.errors.append(SemError(f"redefinition of method {method.name} in class {class_.name}", line=1, column=1))
      else:
        class_.methods_table_pointer[method.name] = method

      method.formals_table_pointer = {"self": class_}
      for formal in method.formals:
          # save method in formal
          formal.method = method

          # check params redefinition
          if formal.name in method.formals_table_pointer:
            self.errors.append(SemError(f"redefinition of parameter {formal.name} in method {method.name}", line=1, column=1))
          else:
            method.formals_table_pointer[formal.name] = formal
      
      # check return type

      # check overridden methods
      

  def check_expression(self, class_):
    pass

  def check_main(self, program):
    pass

  def semantic_analysis(self, program):
    self.errors = []
    self.program = program

    print("check_redefine")
    self.check_redefine()
    print("check_inheritance")
    self.check_inheritance()

    print("DONE")
    return self.program, self.errors


