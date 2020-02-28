import ply.lex as lex
from ply.lex import TOKEN


reserved = {

    'and' : 'and',
    'extends' : 'extends',
    'isnull' : 'isnull',
    'then' : 'then',
    'bool' : 'bool',
    'false' : 'false',
    'let' : 'let',
    'true' : 'true',
    'class' : 'class',
    'if' : 'if',
    'new' : 'new',
    'unit' : 'unit',
    'do' : 'do',
    'in' : 'in',
    'not' : 'not',
    'while' : 'while',
    'else' : 'else',
    'int32' : 'int32',
    'string' : 'string'

}



#list of all token names

tokens = [

    'lowercase_letter',
    'uppercase_letter',
    'letter',
    'bin_digit',
    'digit',
    'hex_digit',

    'lbrace',
    'rbrace',
    'lpar',
    'rpar',
    'colon',
    'semicolon',
    'comma',
    'plus',
    'minus',
    'times',
    'div',
    'pow',
    'dot',
    'equal',
    'lower',
    'lower_equal',
    'assign'

] + list(reserved.values())

#Regular expression simple rules tokens

t_lowercase_letter = r'([a-z])'
t_uppercase_letter = r'([A-Z])'
t_letter= r'(' + t_lowercase_letter + r'|' + t_uppercase_letter + r')'
t_bin_digit = r'[0-1]'
t_digit = r'(' + t_bin_digit + r'|[2-9])'
t_hex_digit=r'('+t_digit+r'|[A-Fa-f])'

#Operators
t_lbrace = r'{'
t_rbrace = r'}'
t_lpar = r'\('
t_rpar = r'\)'
t_colon = r':'
t_semicolon = r';'
t_comma = r','
t_plus = r'\+'
t_minus = r'-'
t_times = r'\*'
t_div = r'/'
t_pow = r'\^'
t_dot = r'\.'
t_equal = r'\='
t_lower = r'\<'
t_lower_equal = r'\<\='
t_assign = "\<-"

#Regular expression function rules tokens 
#WARNING All tokens defined by functions are added in the same order as they appear in the lexer file.
#So longer expression first !

def t_newline(t):
     r'\t+'
     t.lexer.lineno += len(t.value)
     


t_ignore  = ' '

def t_error(t):
    print("oups")
    t.lexer.skip(1)

lexer = lex.lex()

lexer.input(".=<<=<-")

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)