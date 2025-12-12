# colablinter

[![PyPI version](https://img.shields.io/pypi/v/colablinter.svg)](https://pypi.org/project/colablinter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**`colablinter`** is an **IPython magic command extension** designed specifically for Jupyter and Google Colab notebooks.

It integrates the high-speed linter **`ruff`** to perform code quality checks and enforce standards directly within Jupyter/Colab cells.

It allows developers to lint and format code on a **cell-by-cell** basis or check the **entire notebook** with simple commands.

## Magic cell Commands

| Command | Type | Description |
| :--- | :--- | :--- |
| **`%%cl_fix`** | Cell Magic | Fixes and Formats the current cell's code. |
| **`%%cl_report`** | Cell Magic | Displays a linting report for the current cell. |
| **`%cl_autofix`** | Line Magic | Activates or deactivates automatic code fixing and formatting before every cell execution. |
| **`%cl_report`** | Line Magic | Displays a linting report for the **entire saved notebook** (requires Google Drive mount). |

After executing a cell magic command, the fixed/reported code is immediately executed (if applicable), maintaining the notebook workflow.

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

    `%%cl_fix` corrects code and runs the formatter. The cell executes the fixed code.
    ```python
    %%cl_fix
    import sys
    import os
    def calculate_long_sum(a,b,c,d,e,f):
        return {"a":a,"b":b, "sum":(a+b+c)*(d+e+f)}
    ```

    Fixed Cell:
    ```python
    import os
    import sys


    def calculate_long_sum(a, b, c, d, e, f):
        return {"a": a, "b": b, "sum": (a + b + c) * (d + e + f)}
    ```



2. Check cell quality (`%%cl_report`)

    Use `%%cl_report` to see linting reports for the code below the command.
    ```python
    %%cl_report

    def invalid_code(x):
        return x + y # 'y' is not defined
    ```

    Output:
    ```bash
    [ColabLinter:INFO] F821 Undefined name `y`
    --> notebook_cell.py:2:16
    |
    1 | def invalid_code(x):
    2 |     return x + y # 'y' is not defined
    |                  ^
    |

    Found 1 error.
    ```
    Note: After the report is displayed, the code in the cell executes as normal. If errors exist (like F821), execution will fail.

3. Check entire notebook (`%cl_report`)

    Use line magic `%cl_report` to check across the entire saved notebook file (requires the notebook to be saved to Google Drive and mounted).

    ```python
    %cl_report
    ```

4. Activate/Deactivate Auto Fix (`%cl_autofix`)
    The `%cl_autofix` line magic allows you to automatically fix code before every code cell is executed.

    To Activate Auto Fixing:
    ```python
    %cl_autofix on # %cl_autofix off when you want to deactivate
    ```

## Known Caveats & Troubleshooting

Magic Command Execution: When using `%%cl_report` or `%%cl_fix` with `%cl_autofix` on active, the autofix mechanism is temporarily suppressed during the final execution step to prevent infinite loops or dual checks. If you want to disable auto-fixing, use `%cl_autofix off`
