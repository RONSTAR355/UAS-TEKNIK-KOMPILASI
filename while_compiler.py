python_code = '''import re

# ==========================================
# 1. ANALISIS LEKSIKAL (LEXER)
# ==========================================
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"({self.type}, '{self.value}')"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.rules = [
            ('WHILE',    r'\\bwhile\\b'),
            ('ID',       r'\\b[a-zA-Z_][a-zA-Z0-9_]*\\b'),
            ('NUM',      r'\\b\\d+\\b'),
            ('REL_OP',   r'==|!=|<=|>=|<|>'),
            ('ARITH_OP', r'\\+|\\-|\\*|/'),
            ('ASSIGN',   r'='),
            ('LPAREN',   r'\\('),
            ('RPAREN',   r'\\)'),
            ('LBRACE',   r'\\{'),
            ('RBRACE',   r'\\}'),
            ('SEMI',     r';'),
            ('SKIP',     r'[ \\t\\n]+'),
            ('MISMATCH', r'.'),
        ]

    def tokenize(self):
        combined_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules)
        for mo in re.finditer(combined_regex, self.text):
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Karakter tak valid: '{value}'")
            else:
                self.tokens.append(Token(kind, value))
        return self.tokens

# ==========================================
# 2. ANALISIS SINTAKSIS (PARSER & AST)
# ==========================================
class ASTNode: pass

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class AssignmentNode(ASTNode):
    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected):
        token = self.current_token()
        if token and token.type == expected:
            self.pos += 1
            return token
        raise SyntaxError(f"Ekspektasi '{expected}', ditemukan '{token.value if token else 'EOF'}'")

    def parse(self):
        # Format tata bahasa: while ( condition ) { statements }
        self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.parse_condition()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = self.parse_body()
        self.consume('RBRACE')
        return WhileNode(condition, body)

    def parse_condition(self):
        left = VariableNode(self.consume('ID').value)
        op = self.consume('REL_OP').value
        right_tok = self.current_token()
        right = VariableNode(self.consume('ID').value) if right_tok.type == 'ID' else LiteralNode(self.consume('NUM').value)
        return BinaryOpNode(left, op, right)

    def parse_body(self):
        statements = []
        while self.current_token() and self.current_token().type == 'ID':
            var_name = self.consume('ID').value
            self.consume('ASSIGN')
            
            left_tok = self.current_token()
            left_expr = self.consume('ID' if left_tok.type == 'ID' else 'NUM')
            left_node = VariableNode(left_expr.value) if left_tok.type == 'ID' else LiteralNode(left_expr.value)
            
            if self.current_token() and self.current_token().type == 'ARITH_OP':
                op = self.consume('ARITH_OP').value
                right_tok = self.current_token()
                right_expr = self.consume('ID' if right_tok.type == 'ID' else 'NUM')
                right_node = VariableNode(right_expr.value) if right_tok.type == 'ID' else LiteralNode(right_expr.value)
                expr = BinaryOpNode(left_node, op, right_node)
            else:
                expr = left_node
                
            self.consume('SEMI')
            statements.append(AssignmentNode(var_name, expr))
        return statements

# ==========================================
# 3. ANALISIS SEMANTIK
# ==========================================
class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def check(self, node):
        if isinstance(node, WhileNode):
            self.check(node.condition)
            for stmt in node.body:
                self.check(stmt)
        elif isinstance(node, BinaryOpNode):
            self.check(node.left)
            self.check(node.right)
        elif isinstance(node, AssignmentNode):
            if node.variable not in self.symbol_table:
                raise NameError(f"Error Semantik: Variabel '{node.variable}' belum dideklarasikan!")
            self.check(node.expr)
        elif isinstance(node, VariableNode):
            if node.name not in self.symbol_table:
                raise NameError(f"Error Semantik: Variabel '{node.name}' belum dideklarasikan!")

# ==========================================
# 4. GENERASI KODE ANTARA (TAC)
# ==========================================
class TACGenerator:
    def __init__(self):
        self.label_count = 0
        self.temp_count = 0
        self.code = []

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, node):
        if isinstance(node, WhileNode):
            start_label = self.new_label()
            end_label = self.new_label()
            
            self.code.append(f"{start_label}:")
            cond_res = self.generate_expr(node.condition)
            self.code.append(f"ifFalse {cond_res} goto {end_label}")
            
            for stmt in node.body:
                self.generate(stmt)
                
            self.code.append(f"goto {start_label}")
            self.code.append(f"{end_label}:")
        elif isinstance(node, AssignmentNode):
            expr_res = self.generate_expr(node.expr)
            self.code.append(f"{node.variable} = {expr_res}")

    def generate_expr(self, expr_node):
        if isinstance(expr_node, VariableNode):
            return expr_node.name
        elif isinstance(expr_node, LiteralNode):
            return expr_node.value
        elif isinstance(expr_node, BinaryOpNode):
            left = self.generate_expr(expr_node.left)
            right = self.generate_expr(expr_node.right)
            
            if expr_node.op in ['<', '>', '==', '!=', '<=', '>=']:
                return f"{left} {expr_node.op} {right}"
            else:
                temp = self.new_temp()
                self.code.append(f"{temp} = {left} {expr_node.op} {right}")
                return temp

# ==========================================
# SIMULASI PROGRAM UTAMA
# ==========================================
if __name__ == "__main__":
    # 1. Definisi Source Code
    source_code = "while ( i < 10 ) { a = a + 5; i = i + 1; }"
    print(f"SOURCE CODE:\\n{source_code}\\n")

    # 2. Lexical Analysis
    print("--- 1. TAHAP ANALISIS LEKSIKAL (TOKEN) ---")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print(tokens, "\\n")

    # 3. Syntax Analysis
    print("--- 2. TAHAP ANALISIS SINTAKSIS (AST) ---")
    parser = Parser(tokens)
    ast_root = parser.parse()
    print("✓ Abstract Syntax Tree (AST) berhasil dibangun.\\n")

    # 4. Semantic Analysis
    print("--- 3. TAHAP ANALISIS SEMANTIK ---")
    # Asumsi 'i' dan 'a' sudah dideklarasikan sebelumnya
    symbol_table = {"i": "int", "a": "int"} 
    analyzer = SemanticAnalyzer(symbol_table)
    analyzer.check(ast_root)
    print("✓ Analisis semantik selesai, tidak ada variabel yang tidak dikenali.\\n")

    # 5. TAC Generation
    print("--- 4. TAHAP GENERASI KODE ANTARA (TAC) ---")
    tac_gen = TACGenerator()
    tac_gen.generate(ast_root)
    for line in tac_gen.code:
        print(line)
'''

md_code = '''# Tugas Proyek Akhir: Representasi Tahapan Kompilasi

## 📌 Deskripsi Tugas
Proyek ini merupakan implementasi dan simulasi dari tahapan-tahapan utama dalam proses kompilasi (*compiler*). Tahapan yang disimulasikan meliputi:
1. **Analisis Leksikal (*Lexical Analysis*)**
2. **Analisis Sintaksis (*Syntax Analysis*)**
3. **Analisis Semantik (*Semantic Analysis*)**
4. **Generasi Kode Antara (*Intermediate Code Generation* / TAC)**

---

## 🏗️ Pilihan Konstruksi: Perulangan `while`
Konstruksi sintaksis yang dipilih untuk proyek ini adalah perulangan **`while`** (*while-loop*). Konstruksi ini dipilih karena membutuhkan representasi alur kontrol yang menarik, melibatkan evaluasi kondisi berulang dan loncatan (*jump*) instruksi.

### 📜 Pola Tata Bahasa (*Grammar* / BNF)
Pola sintaksis didefinisikan menggunakan pendekatan *Backus-Naur Form* (BNF) sederhana sebagai berikut: