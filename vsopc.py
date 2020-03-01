#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# vsop.py
#
# VSOP Main
#
#
# -----------------------------------------------------------------------------

__author__  = "Adrien and Kevin"
__version__ = '1.0'

import sys
from vsop_lexer import VsopLexer

class Style:
    OK = '\033[92m'
    WARNING = '\x1b[93m'
    ERROR = '\033[91m'
    ENDC = '\x1b[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def output(tokens):
    for t in tokens:
        if(t.type == "type_identifier"):
            print(t.lineno,",",t.column,",type-identifier,",t.value,sep='')
        elif(t.type == "object_identifier"):
            print(t.lineno,",",t.column,",object-identifier,",t.value,sep='')
        elif(t.type == "integer_literal"):
            print(t.lineno,",",t.column,",integer-literal,",t.value,sep='')
        elif(t.type == "string_literal"):
            print(t.lineno,",",t.column,",string-literal,",repr(t.value),sep='')
        else:
            print(t.lineno,",",t.column,",",t.type,sep='')


def main(argv):
    phase = 0
    files = []

    for arg in argv:
        if arg == '-h':
            print("vsop.py -lex <inputfile>")
            exit()
        elif arg in ("-lex", "--lexer"):
            phase = 1
        else:
            files.append(arg)

    if phase != 1:
        print(Style.WARNING + "The only available for now is the lexer"
            + Style.ENDC)
        print("vsop.py -lex <inputfile>")
        exit(1)
    if not files:
        print(Style.WARNING + "You must provide at least one file" + Style.ENDC)
        print("vsop.py -lex <inputfile>")
        exit(1)

    for f in files:
        with open(f, 'r') as file:
            input = file.read()

        # well... no other option for the moment so go lexer i choose you
        lexer = VsopLexer()
        tokens = lexer.tokenize(input)
        output(tokens)
        # for t in tokens:
        #     output(t)
            #print(t.lineno,",",t.column,",",t.type,",",t.value)

if __name__ == "__main__":
    main(sys.argv[1:])
