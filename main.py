import lexer
import transpiler
import argparse

parser = argparse.ArgumentParser(description="Transpile CustomPython to C++")
parser.add_argument("file", type=str, help="File to transpile")
args = parser.parse_args()

currentLexer = lexer.CustomPythonLexer(args.file)
transpiler.Transpile(currentLexer.doLexing())
