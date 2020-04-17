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
          

  def check_fields(self, class_):
    pass

  def check_methods(self, class_):
    pass

  def check_expression(self, class_):
    pass

  def semantic_analysis(self, program):
    self.errors = []
    self.program = program
    self.defined_classes = {}

    print("check_redefine")
    self.defined_classes = self.check_redefine(self.program)
    print("check_inheritance")
    self.check_inheritance(self.program)

    print("DONE")
    return self.program, self.errors


