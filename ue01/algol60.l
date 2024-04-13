%option yylineno
%option noyywrap

%{
#include <stdio.h>
#include <stdlib.h>
#define PRINT_TOKEN(type) printf("  (" #type " %s)\n", yytext);
%}

DIGIT [0-9]
HEXDIGIT [0-9a-fA-F]
NUMBER (0|0x|0b)?{HEXDIGIT}+
ALPHA [a-zA-Z]
ALPHANUM {ALPHA}|{DIGIT}
IDENT (_|{ALPHA})(_|{ALPHANUM})*
COMMENT comment[^;]*;
STRING \"([^\n"]|\\\")*\"
ASSIGN :=
OPERATOR [-+*/]
DELIM [,;()]
WHITESPACE [ \t\r\n]
KEYWORD begin|end|for|step|until|do|procedure

%%
{COMMENT} {}
{WHITESPACE} {}
{KEYWORD} { PRINT_TOKEN(keyword) }
{STRING} { PRINT_TOKEN(string) }
{NUMBER} { PRINT_TOKEN(number) }
{IDENT} { PRINT_TOKEN(identifier) }
{ASSIGN} { PRINT_TOKEN(assignment) }
{OPERATOR} { PRINT_TOKEN(operator) }
{DELIM} { PRINT_TOKEN(delimiter) }
%%

int main() {
    printf("(\n");
    yylex();
    printf(")\n");
    return 0;
}