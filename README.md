# Pseudocode to Python

A small, dependency-free command-line converter for common classroom-style pseudocode. It translates a defined subset of pseudocode; it is not an AI translator and cannot infer ambiguous intent.

## Run it

Convert a file and print the Python:

```bash
python pseudocode_to_python.py example.pseudo
```

Read from standard input:

```bash
cat example.pseudo | python pseudocode_to_python.py
```

Write the converted program to a file:

```bash
python pseudocode_to_python.py example.pseudo --output example.py
```

## Supported syntax

- `SET name TO expression`, `name <- expression`, `name := expression`, and `name = expression`
- `INPUT name` (reads text using Python's `input()`)
- `OUTPUT expression`, `DISPLAY expression`, and `PRINT expression`
- `IF condition THEN` / `ELSE` / `ENDIF`
- `WHILE condition DO` / `ENDWHILE`
- `FOR i FROM start TO end [STEP step]` / `ENDFOR` (the end value is included)
- `REPEAT` / `UNTIL condition`
- `AND`, `OR`, `NOT`, `MOD`, `DIV`, `TRUE`, `FALSE`, and `<>`
- Blank lines and whole-line `#` or `//` comments

Other lines are passed through as Python, so Python expressions and statements can be mixed in. Indentation is determined by the block keywords. Input expressions are not type-inferred: convert input to a number yourself when needed, for example `age = int(input())` in a Python passthrough line.

## Example

Input:

```text
INPUT count
IF count > 0 THEN
    OUTPUT "positive"
ELSE
    OUTPUT "not positive"
ENDIF
```

Output:

```python
count = input()
if count > 0:
    print("positive")
else:
    print("not positive")
```

This is intentionally a small converter. Pseudocode conventions vary, so adjust the input to the syntax above when a construct is not recognized.
