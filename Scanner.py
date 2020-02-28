import ply.lex as lex
from ply.lex import TOKEN


states = (
    ('comment','exclusive'),
)

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
    'assign',

    'integer_literal',
    'type_identifier',
    'object_identifier'

] + list(reserved.values())

#Regular expression simple rules tokens

t_lowercase_letter = r'([a-z])'
t_uppercase_letter = r'([A-Z])'
t_letter = t_lowercase_letter + r'|' + t_uppercase_letter
t_bin_digit = r'([0-1])'
t_digit = t_bin_digit + r'|[2-9]'
t_hex_digit = t_digit+r'|[A-Fa-f]'
t_type_identifier = t_uppercase_letter+r'('+t_letter+r'|'+t_digit+r'| _ )*'


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
t_assign = r'\<-'

#Regular expression for @TOKEN
basetendigit = r'('+ t_digit + r'('+t_digit+r')*)'
basesixteendigit =r'(('+t_hex_digit+r')('+t_hex_digit+r')*)'
integer_literal =  r'0x'+ basesixteendigit +r'|'+ basetendigit
object_identifier = t_lowercase_letter+r'('+t_letter+r'|'+t_digit+r'| _ )*'


#Regular expression function rules tokens
#WARNING All tokens defined by functions are added in the same order as they appear in the lexer file.
#So longer expression first !

# COMMENTS

nb_comments = 0
@TOKEN(r'//.*')
def t_SINGLE_LINE_COMMENT(t):
    pass

@TOKEN(r'\(\*')
def t_OPEN_COMMENT(t):
    global nb_comments
    nb_comments = 1
    t.lexer.begin('comment')

@TOKEN(r'\(\*')
def t_comment_OPEN_COMMENT(t):
    global nb_comments
    nb_comments = nb_comments + 1
    pass

@TOKEN(r'\*\)')
def t_comment_CLOSE_COMMENT(t):
    global nb_comments
    if nb_comments > 1:
        nb_comments = nb_comments - 1
    else:
        t.lexer.begin('INITIAL')

@TOKEN(r'.')
def t_comment_ELSE(t):
    pass

@TOKEN(r'\*\)')
def t_CLOSE_COMMENT(t):
    raise LexError('error', token=t)



@TOKEN(object_identifier)
def t_object_identifier(t):
     t.type = reserved.get(t.value,'object_identifier')
     return t

@TOKEN(integer_literal)
def t_integer_literal(t):
    if(t.value[:2]==r'0x'):
        t.value=int(t.value,0)
    else:
        t.value=int(t.value)
    return t

def t_newline(t):
     r'\n'
     t.lexer.lineno += len(t.value)

def t_comment_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t\r\f'
t_comment_ignore = ''

def t_error(t):
    print("oups")
    t.lexer.skip(1)

def t_comment_error(t):
    return t_error(t)

lexer = lex.lex()

lexer.input(".=<<=<-(*(*a*)b*)=\n")

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
