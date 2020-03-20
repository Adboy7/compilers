# -----------------------------------------------------------------------------
# vsop_parser.py
#
# VSOP parser
#
# parser == yacc
#
# REF:
#
# -----------------------------------------------------------------------------
__author__  = "Adrien and Kevin"
__version__ = '1.0'

import ply.lex as lex

class ParseError(Exception):
  def __init__(self, line, column, message):
    self.line = line
    self.column = column
    self.message = message


class VsopParser:
  def __init__(self):
    pass

  def parse(self):
    pass

  