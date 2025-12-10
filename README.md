# colablinter

[![PyPI version](https://img.shields.io/pypi/v/colablinter.svg)](https://pypi.org/project/colablinter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**`colablinter`** is an **IPython magic command extension** designed specifically for Jupyter and Google Colab notebooks.

It integrates the high-speed linter **`ruff`** and import sorter **`isort`** to perform code quality checks, fix issues, and enforce formatting standards.

It allows developers to lint and format code on a **cell-by-cell** basis or check the **entire notebook** with simple commands.

## Magic cell Commands

| Command | Type | Role | Description |
| :--- | :--- | :--- | :--- |
| **`%%cl_check`** | Cell Magic | Quality Check | Displays a linting report for the **current cell's code**. |
| **`%%cl_format`** | Cell Magic | Format Preview | **Formats the current cell's code** and displays the result for manual application (copy/paste). |
| **`%cl_check`** | Line Magic | Quality Check | Displays a linting report for the **entire saved notebook** (requires Google Drive mount). |

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

1. Check cell quality (`%%cl_check`)

    Use `%%cl_check` to see linting reports for the code below the command.
    ```python
    %%cl_check

    def invalid_code(x):
        return x + y # 'y' is not defined
    ```

    Output examples:
    ```bash
    ---- Code Quality & Style Check Report ----
    F821 Undefined name `y`
    --> notebook_cell.py:3:16
    |
    2 | def invalid_code(x):
    3 |     return x + y # 'y' is not defined
    |                  ^
    |

    Found 1 error.
    -------------------------------------------
    ```
    Note: After the report is displayed, the code in the cell executes as normal. If errors exist (like F821), execution will fail.

2. Format cell preview (`%%cl_format`)

    `%%cl_format` runs the formatter and displays the corrected code. The cell executes the original code, so you must copy the formatted output and paste it back into the cell to apply the changes.

    ```python
    %%cl_format
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

3. Check entire notebook (`%cl_check`)

    Use line magic `%cl_check` to check across the entire saved notebook file (requires the notebook to be saved to Google Drive and mounted).

    ```python
    %cl_check
    ```
