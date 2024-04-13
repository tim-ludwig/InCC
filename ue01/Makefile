default: lexer.exe

lexer.exe: lex.yy.c
	gcc -Il lex.yy.c -o lexer.exe

lex.yy.c: algol60.l
	flex algol60.l

.PHONY: clean
clean:
	rm lex.yy.c lexer.exe

.PHONY: run
run: lexer.exe
	./lexer.exe < factorial.alg