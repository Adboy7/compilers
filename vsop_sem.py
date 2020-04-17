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
  def __init__(self, message, line=None, column=None, token=None, expected=None):
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
    for c in program.list_class:
      if c.name in self.defined_classes:
        self.errors.append(SemError("Class already defined", line=0, column=0))
      else:
        self.defined_classes[c.name] = c

  def check_inheritance(self, class_):
    pass

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

    self.check_redefine(self.program)

    return self.program, self.errors


