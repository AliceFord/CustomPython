import lexer
import transpiler

currentLexer = lexer.CustomPythonLexer("input/primeSieve.txt")
transpiler.Transpile(currentLexer.doLexing()).run()
