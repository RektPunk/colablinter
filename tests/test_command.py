import inspect

from colablinter.command import (
    cell_check,
    cell_check_fix,
    cell_check_unsafe_fix,
    cell_format,
)


def test_cell_check_real():
    # Code with a real linting error (F541: f-string without placeholders)
    bad_code = "f'test'"
    report = cell_check(bad_code)
    assert report is not None
    assert "F541" in report


def test_cell_check_clean_real():
    clean_code = "x = 1"
    assert cell_check(clean_code) is None


def test_cell_check_fix_real():
    # Code that can be fixed automatically (F541)
    code = "f'test'"
    fixed = cell_check_fix(code)
    assert fixed == "'test'"


def test_cell_check_unsafe_fix_real():
    # Unsafe fix: F632 (is comparison to literal)
    code = "x is 'a'"
    fixed = cell_check_unsafe_fix(code)
    assert fixed == "x == 'a'"


def test_cell_format_real():
    # Formatting: messy spacing
    code = "x=1+2"
    formatted = cell_format(code)
    assert formatted == "x = 1 + 2"


def test_cell_check_ignore_f401():
    # F401 should be ignored even in complex cases
    # We must sort imports as Ruff expects to avoid I001 error
    code = inspect.cleandoc("""
        import os
        import sys
        from datetime import datetime

        x = 1
    """)
    assert cell_check(code) is None


def test_cell_check_ignore_f821():
    # F821 should be ignored (e.g., variables defined in previous Jupyter cells)
    code = inspect.cleandoc("""
        # df and model are assumed to be defined in a previous cell
        result = df.merge(other_df, on="id")
        predictions = model.predict(result)
    """)
    assert cell_check(code) is None


def test_cell_check_unsafe_fix_multiline():
    # SIM105 (Use contextlib.suppress)
    code = inspect.cleandoc("""
        try:
            os.remove("file.txt")
        except OSError:
            pass
    """)
    fixed = cell_check_unsafe_fix(code)
    assert fixed is not None
    assert "contextlib.suppress" in fixed


def test_cell_format_complex():
    # Complex formatting: nested lists, dicts, and long lines
    code = "d={'a':1,'b':[1,2,3],'c':{'d':4}} #comment"
    formatted = cell_format(code)
    expected = """d = {"a": 1, "b": [1, 2, 3], "c": {"d": 4}}  # comment"""
    assert formatted == expected


def test_preserve_strings_and_comments():
    # Ensure that linting/formatting doesn't mess up strings or comments
    code = inspect.cleandoc("""
        def greet():
            \"\"\"This is a docstring with == None inside.\"\"\"
            s = "x == None" # literal string
            # real comment: x == None
            return s
    """)
    # cell_check should find NO issues because E711 shouldn't trigger inside strings/comments
    assert cell_check(code) is None


def test_cell_check_unsafe_fix_complex():
    # Complex unsafe fix: SIM102 (Nested if statements)
    code = inspect.cleandoc("""
        if a:
            if b:
                pass
    """)
    fixed = cell_check_unsafe_fix(code)
    assert fixed is not None
    assert "if a and b:" in fixed
