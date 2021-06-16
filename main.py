import lexer
import transpiler

currentLexer = lexer.CustomPythonLexer("input/main.cpy")
transpiler.Transpile(currentLexer.doLexing()).run()
