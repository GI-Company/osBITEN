// OBPL Language Syntax Definition
typedef enum {
    TOKEN_IDENTIFIER,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_KEYWORD,
    TOKEN_OPERATOR,
    TOKEN_SYMBOL,
    TOKEN_EOF
} TokenType;

// Keywords
const char* OBPL_KEYWORDS[] = {
    "func", "var", "const", "if", "else", "while", "for",
    "return", "break", "continue", "class", "module",
    "import", "export", "async", "await", "try", "catch",
    "struct", "enum", "unsafe", "native", "syscall"
};