# Tugas Proyek Akhir: Representasi Tahapan Kompilasi

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

```text
<while_stmt>     ::= "while" "(" <condition> ")" "{" <statement_list> "}"
<condition>      ::= <expression> <rel_op> <expression>
<expression>     ::= <identifier> | <number>
<rel_op>         ::= "<" | ">" | "==" | "!=" | "<=" | ">="
<statement_list> ::= <statement> | <statement> <statement_list>
<statement>      ::= <assignment> ";"
<assignment>     ::= <identifier> "=" <expression> <arith_op> <expression> 
                   | <identifier> "=" <expression>
<arith_op>       ::= "+" | "-" | "*" | "/"
```

---

## ⚙️ Penjelasan Implementasi (Tahapan Kompilasi)
Seluruh proses kompilasi direpresentasikan menggunakan bahasa pemrograman **Python** (dapat dilihat pada berkas `while_compiler.py`). Berikut adalah penjelasan untuk tiap tahapan:

### 1. Analisis Leksikal (*Lexer*)
* **Tugas:** Membaca kode sumber (*source code*) berupa teks mentah dan memecahnya menjadi kumpulan **Token**.
* **Implementasi:** Menggunakan *Regular Expression* (Regex) di Python untuk mencocokkan pola string menjadi token seperti `WHILE`, `ID` (variabel), `NUM` (angka), `REL_OP` (operator relasional), kurung `LPAREN`/`RPAREN`, dan sebagainya. Spasi kosong diabaikan.

### 2. Analisis Sintaksis (*Parser*)
* **Tugas:** Menerima *array* token dari tahap leksikal dan memeriksa apakah urutannya sesuai dengan tata bahasa (BNF) yang didefinisikan.
* **Implementasi:** Membuat parser sederhana (*Recursive Descent Parser*) yang membaca token demi token, memvalidasi struktur `while (...) { ... }`, dan jika valid, membangun **Abstract Syntax Tree (AST)**. AST dipetakan menjadi objek hierarki (misal: `WhileNode`, `AssignmentNode`, `BinaryOpNode`).

### 3. Analisis Semantik
* **Tugas:** Memastikan program memiliki makna yang valid. Salah satu fungsi utamanya adalah mengecek deklarasi variabel.
* **Implementasi:** Menggunakan simulasi **Tabel Simbol (*Symbol Table*)**. Node AST ditelusuri (*traversal*), dan sistem akan mengecek apakah variabel yang digunakan (baik di kondisi maupun assignment) sudah terdefinisi di Tabel Simbol. Jika ada variabel yang tidak dikenali (siluman), kompilator akan menghasilkan `NameError`.

### 4. Generasi Kode Antara (*Three-Address Code / TAC*)
* **Tugas:** Menerjemahkan AST menjadi bahasa perantara tingkat rendah (instruksi linier maksimal tiga alamat) sebelum dikonversi menjadi bahasa perakitan/mesin.
* **Implementasi:** `TACGenerator` mengubah instruksi kontrol aliran `while` menjadi operasi berbasis label. TAC yang dihasilkan memuat:
  * Label mulai (contoh: `L1`)
  * Evaluasi loncatan bersyarat (*conditional jump*: `ifFalse ... goto L2`)
  * Eksekusi isi blok dengan variabel sementara (`t1`, `t2`)
  * Lompatan kembali tanpa syarat (*unconditional jump*: `goto L1`)
  * Label akhir / terminasi (contoh: `L2`)

---

## 🚀 Cara Menjalankan Program & Contoh Output

Pastikan Python 3.x telah terinstal, lalu jalankan perintah berikut di terminal:
```bash
python while_compiler.py
```

**Contoh *Source Code* Target:**
```text
while ( i < 10 ) { a = a + 5; i = i + 1; }
```

**Hasil Execusi Program:**
```text
SOURCE CODE:
while ( i < 10 ) { a = a + 5; i = i + 1; }

--- 1. TAHAP ANALISIS LEKSIKAL (TOKEN) ---
[(WHILE, 'while'), (LPAREN, '('), (ID, 'i'), (REL_OP, '<'), (NUM, '10'), (RPAREN, ')'), (LBRACE, '{'), (ID, 'a'), (ASSIGN, '='), (ID, 'a'), (ARITH_OP, '+'), (NUM, '5'), (SEMI, ';'), (ID, 'i'), (ASSIGN, '='), (ID, 'i'), (ARITH_OP, '+'), (NUM, '1'), (SEMI, ';'), (RBRACE, '}')] 

--- 2. TAHAP ANALISIS SINTAKSIS (AST) ---
✓ Abstract Syntax Tree (AST) berhasil dibangun.

--- 3. TAHAP ANALISIS SEMANTIK ---
✓ Analisis semantik selesai, tidak ada variabel yang tidak dikenali.

--- 4. TAHAP GENERASI KODE ANTARA (TAC) ---
L1:
ifFalse i < 10 goto L2
t1 = a + 5
a = t1
t2 = i + 1
i = t2
goto L1
L2:
```
