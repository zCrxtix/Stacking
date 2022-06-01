import sys

EXTENSION = ".stack"

WHITESPACE = " \n\t\r"
DIGITS     = "0123456789"
LETTERS    = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
KEYWORDS   = ["print"]

def Error(file, line, col, err):
    print(f"{file}:{line}:{col}: {err}")
    sys.exit(1)

class Lexer:
    def __init__(self, file, text):
        self.file = file
        self.text = text
        self.tokens = []
        self.pos = -1
        self.line = 1
        self.col = 0
        self.char = "<eof>"
        self.next()
    def next(self):
        self.pos += 1
        self.col += 1
        if self.pos >= len(self.text):
            self.char = "<eof>"
        else:
            self.char = self.text[self.pos]
        if self.char == "\n":
            self.line += 1
            self.col = 0
            
    def lex_number(self):
        res = ""
        dot_ct = 0
        while self.char in DIGITS:
            res += self.char
            if self.char == ".":
                dot_ct += 1
            if dot_ct > 1:
                Error(self.file, self.line, self.col, "Illegal number")
            self.next()
        self.pos -= 1
        self.col -= 1
        if dot_ct == 0:
            return ["NUMBER", int(res), self.line, self.col, self.file]
        return ["NUMBER", float(res), self.line, self.col, self.file]
    def lex_identifier(self):
        identifier = ""
        while self.char != "<eof>" and self.char in LETTERS:
            identifier += self.char
            self.next()
        self.pos -= 1
        self.col -= 1
        if identifier in KEYWORDS:
            return ["KEYWORD", identifier, self.line, self.col, self.file]
        else:
            return ["IDENTIFIER", identifier, self.line, self.col, self.file]
    def comment(self):
        while self.char != "<eof>" and self.char != "\n":
            self.next()

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.pos = -1
        self.next()
    def next(self):
        self.pos += 1
        if self.pos >= len(self.tokens):
            self.token = ["<eof>", "eof", self.lexer.tokens[-1][2], self.lexer.tokens[-1][3], self.lexer.tokens[-1][4]]
        else:
            self.token = self.tokens[self.pos]

def lex(file, text):
    lexer = Lexer(file, text)
    while lexer.char != "<eof>":
        if lexer.char in WHITESPACE:
            lexer.next()
        elif lexer.char in DIGITS:
            lexer.tokens.append(lexer.lex_number())
            lexer.next()
        elif lexer.char in LETTERS:
            lexer.tokens.append(lexer.lex_identifier())
            lexer.next()
        elif lexer.char == "+":
            lexer.tokens.append(["ADD", lexer.char, lexer.line, lexer.col, file])
            lexer.next()
        elif lexer.char == "-":
            lexer.tokens.append(["MIN", lexer.char, lexer.line, lexer.col, file])
            lexer.next()
        elif lexer.char == "*":
            lexer.tokens.append(["MUL", lexer.char, lexer.line, lexer.col, file])
            lexer.next()
        elif lexer.char == "/":
            lexer.tokens.append(["DIV", lexer.char, lexer.line, lexer.col, file])
            lexer.next()
        elif lexer.char == "!":
            lexer.comment()
            lexer.next()
        else:
            Error(file, lexer.line, lexer.col, f"Illegal character {lexer.char}")
    return lexer

def parse(lexer):
    parser = Parser(lexer)
    program = []
    for token in parser.tokens:
        Type = token[0]
        value = token[1]
        if value == "+":
                program.append(["ADD", None, token[2], token[3], token[4]])
        elif value == "-":
                program.append(["SUB", None, token[2], token[3], token[4]])
        elif value == "*":
                program.append(["MUL", None, token[2], token[3], token[4]])
        elif value == "/":
                program.append(["DIV", None, token[2], token[3], token[4]])
        elif Type == "KEYWORD":
            if value == "print":
                program.append(["PRINT", None, token[2], token[3], token[4]])
            else:
                Error(token[4], token[2], token[3], f"Unreachable")
        elif Type == "NUMBER" or Type == "IDENTIFIER":
            program.append(["PUSH", value, token[2], token[3], token[4]])
        else:
            Error(token[4], token[2], token[3], f"Unreachable")
    return program

def evaluate(program):
    stack = []
    for op in program:
        Type = op[0]
        value = op[1]
        if Type == "PUSH":
            stack.append(value)
        elif Type == "ADD":
            if len(stack) < 2: Error(op[4], op[2], op[3], "Stack underflow")
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif Type == "SUB":
            if len(stack) < 2: Error(op[4], op[2], op[3], "Stack underflow")
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
        elif Type == "MUL":
            if len(stack) < 2: Error(op[4], op[2], op[3], "Stack underflow")
            a = stack.pop()
            b = stack.pop()
            stack.append(a * b)
        elif Type == "DIV":
            if len(stack) < 2: Error(op[4], op[2], op[3], "Stack underflow")
            a = stack.pop()
            b = stack.pop()
            if a == 0: Error(op[4], op[2], op[3], "Zero division")
            stack.append(b / a)
        elif Type == "PRINT":
            if len(stack) < 1: Error(op[4], op[2], op[3], "Stack underflow")
            print("Stacking.stdout - " + str(stack.pop()))

def run(file, stdin):
    code = ""
    debug = False
    if stdin:
        code = input("<Stacking.stdin> - ")
    else:
        with open(file, "r") as f:
            code = f.read()
    lexer = lex("<stdin>", code)
    if debug == True: print(lexer.tokens)

    program = parse(lexer)
    evaluate(program)

def usage():
    print("USAGE: python3 stacking.py [file]")
    print("       python3 stacking.py -stdin")
    print("       python3 stacking.py -help")

def main():
    argv = sys.argv[1:]
    if len(argv) == 0: usage()
    elif "-help" in argv: usage()
    elif "-stdin" in argv: run(None, True)
    else:
        if argv[0].endswith(EXTENSION):
            run(argv[0], False)
        else:
            print("Invalid file type")

        
    
        

if __name__ == '__main__':
    main()