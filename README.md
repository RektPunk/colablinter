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
| **`%%cfix`** | Cell Magic | Fixes and Formats the current cell's code. |
| **`%%creport`** | Cell Magic | Displays a linting report for the current cell. |
| **`%clautofix`** | Line Magic | Activates or deactivates automatic code fixing and formatting before every cell execution. |
| **`%clreport`** | Line Magic | Displays a linting report for the **entire saved notebook** (requires Google Drive mount). |
| **`%%csql`** | Cell Magic | Formats SQL strings within the cell (e.g., query = """..."""). |

After executing a cell magic command, the fixed/reported code is immediately executed (if applicable), maintaining the notebook workflow.

## Installation

Requires Python 3.10 or newer.

```bash
pip install colablinter
```

## Usage
The extension must be explicitly loaded in the notebook session before use.

```python
%load_ext colablinter
```


1. Fix and Format cell (`%%cfix`)

    `%%cfix` corrects code and runs the formatter. The cell executes the fixed code.
    ```python
    %%cfix
    import math, sys;

    class Example(   object ):
        def __init__    ( self, bar ):
          if bar : bar+=1;  bar=bar* bar   ; return bar
          else:
                        some_string = "foo"
                        return (sys.path, some_string)
    ```

    Fixed Cell:
    ```python
    import math
    import sys


    class Example(object):
        def __init__(self, bar):
            if bar:
                bar += 1
                bar = bar * bar
                return bar
            else:
                some_string = "foo"
                return (sys.path, some_string)
    ```
    **Note on F401 (Unused Imports):**
    The linter is explicitly configured to **ignore F401 errors** (unused imports). This is to ensure compatibility with the stateful nature of Jupyter/Colab notebooks, where imports in one cell may be necessary for code execution in subsequent cells, preventing unintended breakage of the notebook's execution flow.

2. Check cell quality (`%%creport`)

    Use `%%creport` to see linting reports for the code below the command.
    ```python
    %%creport

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

3. Activate/Deactivate Auto Fix (`%clautofix`)

    The `%clautofix` line magic allows you to automatically fix code before every code cell is executed.

    To Activate Auto Fixing:
    ```python
    %clautofix on # %clautofix off when you want to deactivate
    ```

4. Check entire notebook (`%clreport`)

    Use line magic `%clreport` to check across the entire saved notebook file (requires the notebook to be saved to Google Drive and mounted).

    ```python
    %clreport /content/drive/MyDrive/Colab Notebooks/path/to/notebook.ipynb
    ```

5. Format SQL strings (`%%csql`)

    The `%%csql` cell magic identifies a specific SQL string variable within the cell and automatically reformats it using `SQLFluff`. It enforces professional SQL standards, such as keyword capitalization and consistent indentation.
    ```python
    %%csql some_query
    some_query = """
    select u.user_id, u.phone_number, u.email, count(o.order_id) as total_orders
    from users u join orders o on u.user_id = o.user_id
    where u.user_id is not null and u.status = 'active' and o.created_at >= '2025-01-01'
    group by u.user_id, u.phone_number, u.email
    order by total_orders desc
    """
    ```

    Fixed cell:
    ```python
    some_query = """
    SELECT
        u.user_id,
        u.phone_number,
        u.email,
        count(o.order_id) AS total_orders
    FROM users AS u INNER JOIN orders AS o ON u.user_id = o.user_id
    WHERE
        u.user_id IS NOT NULL
        AND u.status = 'active'
        AND o.created_at >= '2025-01-01'
    GROUP BY u.user_id, u.phone_number, u.email
    ORDER BY total_orders DESC
    """
    ```

## Known Caveats & Troubleshooting

Magic Command Execution: When using magic or terminal commands with `%clautofix` on active, the autofix mechanism is temporarily suppressed during the final execution step to prevent infinite loops or dual checks. If you want to disable auto-fixing, use `%clautofix off`
