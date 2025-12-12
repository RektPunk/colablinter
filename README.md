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
| **`%%cl_fix`** | Cell Magic | Quality Check | **Fixes and Formats the current cell's code**. |
| **`%%cl_report`** | Cell Magic | Quality Report | Displays a linting report for the current cell. |
| **`%cl_autofix`** | Line Magic | Auto Format | Activates or deactivates automatic code fixing and formatting before every cell execution. |
| **`%cl_report`** | Line Magic | Quality Check | Displays a linting report for the **entire saved notebook** (requires Google Drive mount). |


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


1. Fix and Format cell (`%%cl_fix`)

    `%%cl_fix` corrects code and runs the formatter. The cell executes the original code.

    ```python
    %%cl_format
    import sys
    import os
    def calculate_long_sum(a,b,c,d,e,f):
        return (a+b+c)*(d+e+f)  # messy
    ```

    Replaced code:
    ```python
    import os
    import sys
    from datetime import datetime


    def calculate_long_sum(a, b, c, d, e, f):
        return (a + b + c) * (d + e + f)  # messy
    ```



2. Check cell quality (`%%cl_report`)

    Use `%%cl_report` to see linting reports for the code below the command.
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

3. Check entire notebook (`%cl_report`)

    Use line magic `%cl_report` to check across the entire saved notebook file (requires the notebook to be saved to Google Drive and mounted).

    ```python
    %cl_report
    ```

4. Activate/Deactivate Auto Format (`%cl_autofix`)
    The `%cl_autofix` line magic allows you to automatically format code before every code cell is executed.

    To Activate Auto Formatting:
    ```python
    %cl_autofix on # off when you want to deactivate
    ```
