# colablinter

[![PyPI version](https://img.shields.io/pypi/v/colablinter.svg)](https://pypi.org/project/colablinter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**`colablinter`** is an **IPython magic command extension** for Jupyter and Google Colab environments.

It integrates the high-speed linter **`ruff`** and import sorter **`isort`** to perform cell-by-cell code quality and formatting checks.

## Magic Commands

| Command | Role | Description |
| :--- | :--- | :--- |
| **`%%check`** | **Quality Check** | Displays a linting report. |
| **`%%format`** | **Format, Sort** | Displays a formatting preview (**for copy/paste**) |

After executing a magic command, the **original code** of the cell is executed (if applicable to the command).

## Installation

Requires Python 3.12 or newer.

```bash
pip install colablinter
```

## Usage
The extension must be explicitly loaded in the notebook session before use.

```python
%load_ext colablinter
```

1. Check Code Quality

    Use `%%check` to see linting reports.
    ```python
    %%check

    def invalid_code(x):
        return x + y # 'y' is not defined
    ```

    Output examples:
    ```bash
    --- Code Quality & Style Check Report ---
    F821 Undefined name `y`
    --> notebook_cell.py:4:16
    |
    2 | def invalid_code(x):
    3 |     return x + y # 'y' is not defined
    |                ^
    |

    Found 1 error.
    -------------------------------------------
    ```

2. Format code preview

    `%%format` will display the formatted code, but the cell executes the original code.
    ```python
    %%format
    import sys
    import os
    def calculate_long_sum(a,b,c,d,e,f):
        return (a+b+c)*(d+e+f)  # messy
    ```

    Output examples:
    ```python
    # Formatted Code
    import os
    import sys
    from datetime import datetime


    def calculate_long_sum(a, b, c, d, e, f):
        return (a + b + c) * (d + e + f)  # messy
    ```
