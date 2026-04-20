<div style="text-align: center;">
  <img src="https://capsule-render.vercel.app/api?type=transparent&fontColor=0047AB&text=colablinter&height=120&fontSize=90">
</div>
<p align="center">
  <a href="https://github.com/RektPunk/colablinter/releases/latest">
    <img alt="release" src="https://img.shields.io/github/v/release/RektPunk/colablinter.svg">
  </a>
</p>


## Overview

**`colablinter`** is an **IPython magic command extension** designed for Jupyter and Google Colab notebooks.
It integrates the high-speed linter **`ruff`** to perform code quality checks and formatting directly within Jupyter/Colab cells.
It allows developers to lint code on a **cell-by-cell** basis with simple commands.

## Magic cell Commands

| Command | Description |
| :--- | :--- |
| **`%clautofix`** | Activates or deactivates automatic fix including import sorting, formatting, and execution time display before every cell. |
| **`%%clcheck`** | Displays a linting report for the current cell. |
| **`%%clunsafefix`** | Performs a linting check and applies "unsafe" fixes that might change code logic (e.g., changing mutable default arguments). |

After executing a cell magic command, the checked/formatted code is immediately executed (if applicable), maintaining the notebook workflow.

## Installation

Just run it in colab:
```python
!uv pip install colablinter
```

The extension must be explicitly loaded in the notebook session before use.
```python
%load_ext colablinter
```
Once loaded, `%clautofix` is activated by default to keep your code clean from the start.


## Usage

1. Activate/Deactivate Auto Fix (`%clautofix`)

    The `%clautofix` line magic allows you to automatically fix code before every code cell is executed.

    ```python
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


    class Example:
        def __init__(self, bar):
            if bar:
                bar += 1
                bar = bar * bar
                return bar
            else:
                some_string = "foo"
                return (sys.path, some_string)
    ```

    To deactivate auto fixing:
    ```python
    %clautofix off # %clautofix on when you want to activate
    ```

2. Check cell quality (`%%clcheck`)

    Use `%%clcheck` to see linting reports for the code below the command. After the report is displayed, the code in the cell executes as normal.
    ```python
    %%clcheck

    def invalid_code(x):
        return x + y
    ```

    Output:
    ```bash
    [ColabLinter:INFO] F821 Undefined name `y`
    --> tmp.py:2:16
      |
    1 | def invalid_code(x):
    2 |     return x + y
      |                ^
      |
    Found 1 error.
    [ColabLinter:INFO] ✔ Done | 0.015s
    ```

3. Unsafe Fix (`%%clunsafefix`)

    Use `%%clunsafefix` when you want `ruff` to aggressively clean up your code, including rules that are typically considered risky (like fixing mutable default arguments or complex refactoring).

    ```python
    %%clunsafefix

    def process_data(new_item, current_list=[]):
        if new_item:
            if isinstance(new_item, str):
                current_list.append(new_item)
        if len(current_list) > 0:
            return True
        else:
            return False
    ```

    Output:
    ```python
    def process_data(new_item, current_list=None):
        if current_list is None:
            current_list = []
        if new_item and isinstance(new_item, str):
            current_list.append(new_item)
        return len(current_list) > 0
    ```


## Known Caveats & Troubleshooting

**Note on F401:**
The linter is explicitly configured to **ignore F401 errors** (unused imports). This is to ensure compatibility with the stateful nature of Jupyter/Colab notebooks, where imports in one cell may be necessary for code execution in subsequent cells, preventing unintended breakage of the notebook's execution flow.

Magic Command Execution: When using magic or terminal commands while `%clautofix` is active, the auto-format mechanism is temporarily suppressed during the final execution step to prevent infinite loops or dual checks. If you want to disable auto-formatting, use `%clautofix off`
