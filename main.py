import lexer
import transpiler

currentLexer = lexer.CustomPythonLexer("input/main.txt")
transpiler.Transpile(currentLexer.doLexing()).run()
