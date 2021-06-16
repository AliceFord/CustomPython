import lexer
import transpiler

currentLexer = lexer.CustomPythonLexer("input/primeSieve.cpy")
transpiler.Transpile(currentLexer.doLexing()).run()
