# colablinter

[![PyPI version](https://img.shields.io/pypi/v/colablinter.svg)](https://pypi.org/project/colablinter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**`colablinter`** is an **IPython magic command extension** designed for Jupyter and Google Colab notebooks.
It integrates the high-speed linter **`ruff`** to perform code quality checks and formatting directly within Jupyter/Colab cells.
It allows developers to lint code on a **cell-by-cell** basis or the **entire notebook** with simple commands.

## Magic cell Commands

| Command | Description |
| :--- | :--- |
| **`%%cformat`** | Sorts imports and Formats the current cell's code. |
| **`%%ccheck`** | Displays a linting report for the current cell. |
| **`%clautoformat`** | Activates or deactivates automatic import sorting, formatting, and execution time display before every cell. |
| **`%clcheck`** | Displays a linting report for the **entire saved notebook** (requires Google Drive mount). |

After executing a cell magic command, the checked/formatted code is immediately executed (if applicable), maintaining the notebook workflow.

## Installation

Requires Python 3.10 or newer.

```bash
pip install colablinter
```

## Usage
The extension must be explicitly loaded in the notebook session before use. Once the extension is loaded, `%clautoformat` is activated by default.

```python
%load_ext colablinter
```


1. Sorts imports and Formats cell (`%%cformat`)

    `%%cformat` corrects code and runs the formatter. The cell executes after cell is formatted.
    ```python
    %%cformat
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

2. Check cell quality (`%%ccheck`)

    Use `%%ccheck` to see linting reports for the code below the command. After the report is displayed, the code in the cell executes as normal.
    ```python
    %%ccheck

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
    **Note on F401:**
    The linter is explicitly configured to **ignore F401 errors** (unused imports). This is to ensure compatibility with the stateful nature of Jupyter/Colab notebooks, where imports in one cell may be necessary for code execution in subsequent cells, preventing unintended breakage of the notebook's execution flow.

3. Activate/Deactivate Auto Fix (`%clautoformat`)

    The `%clautoformat` line magic allows you to automatically fix code before every code cell is executed.

    To Activate Auto Fixing:
    ```python
    %clautoformat on # %clautoformat off when you want to deactivate
    ```

4. Check entire notebook (`%clcheck`)

    Use line magic `%clcheck` to check across the entire saved notebook file (requires the notebook to be saved to Google Drive and mounted).

    ```python
    %clcheck /content/drive/MyDrive/Colab Notebooks/path/to/notebook.ipynb
    ```

## Known Caveats & Troubleshooting

Magic Command Execution: When using magic or terminal commands while `%clautoformat` is active, the auto-format mechanism is temporarily suppressed during the final execution step to prevent infinite loops or dual checks. If you want to disable auto-formatting, use `%clautoformat off`
