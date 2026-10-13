<div style="text-align: center;">
  <img src="https://capsule-render.vercel.app/api?type=transparent&fontColor=0047AB&text=colablinter&height=120&fontSize=90"/>
</div>

**`colablinter`** is an **IPython magic command extension** for Jupyter and Google Colab notebooks. It integrates the fast Python linter and formatter **`ruff`** to check code quality and format code directly within notebook cells. It supports cell-by-cell linting and automatic formatting with simple magic commands. Try it here: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RektPunk/colablinter/blob/main/examples/notebook.ipynb)

## Magic Commands

| Command             | Description                                                                                                                     |
| :------------------ | :------------------------------------------------------------------------------------------------------------------------------ |
| **`%clautofix`**    | Enables or disables automatic fixing and formatting before cell execution, including import sorting and execution time display. |
| **`%%clcheck`**     | Displays a linting report for the current cell before executing it.                                                             |
| **`%%clunsafefix`** | Checks the current cell and applies unsafe fixes that may change code behavior.                                                 |

The cell's code is executed after processing, where applicable, preserving the usual notebook workflow.

## Installation

Install `colablinter` in your Jupyter or Colab environment:

```python
!uv pip install colablinter
```

Load the extension in the notebook session:

```python
%load_ext colablinter
```

Automatic fixing is enabled by default after loading the extension.

## Usage

### 1. Automatic Fixing (`%clautofix`)

The `%clautofix` line magic automatically fixes and formats code before each cell is executed.

**Before:**

```python
import math, sys;

class Example(   object ):
    def __init__    ( self, bar ):
        if bar : bar+=1;  bar=bar* bar
        else:
            some_string = "foo"
            print(some_string, sys.path)
```

**After:**

```python
import math
import sys


class Example:
    def __init__(self, bar):
        if bar:
            bar += 1
            bar = bar * bar
        else:
            some_string = "foo"
            print(some_string, sys.path)
```

To disable automatic fixing:

```python
%clautofix off
```

Re-enable it whenever needed:

```python
%clautofix on
```

### 2. Check Cell Quality (`%%clcheck`)

Use `%%clcheck` to display linting reports for the code in the current cell. The cell is then executed normally.

```python
%%clcheck

def invalid_code(x):
    some_string = "foo"
    return x
```

Example output:

```text
F841 Local variable `some_string` is assigned to but never used
 --> cell:2:5
  |
1 | def invalid_code(x):
2 |     some_string = "foo"
  |     ^^^^^^^^^^^
3 |     return x
  |
help: Remove assignment to unused variable `some_string`
  |
1 | def invalid_code(x):
  -     some_string = "foo"
2 |     return x
  |
note: This is an unsafe fix and may change runtime behavior
```

### 3. Unsafe Fixes (`%%clunsafefix`)

Use `%%clunsafefix` to apply Ruff's unsafe fixes in addition to regular linting fixes. These fixes may change code behavior, so review the result before relying on it.

```python
%%clunsafefix

def process_data(new_item, current_list=[]):
    old_item = "redundant"
    if new_item:
        if isinstance(new_item, str):
            current_list.append(new_item)

    if len(current_list) > 0:
        return True
    else:
        return False
```

**Fixed Cell:**

```python
def process_data(new_item, current_list=None):
    if current_list is None:
        current_list = []
    if new_item and isinstance(new_item, str):
        current_list.append(new_item)

    return len(current_list) > 0
```

## Known Caveats & Troubleshooting

### Ignored Linting Rules

The following Ruff rules are ignored to better support interactive Jupyter and Colab notebooks:

- **F401 (Unused imports):** Allows imports in one cell to be used in subsequent cells.
- **F821 (Undefined names):** Avoids false positives when names are defined in previously executed cells.
- **E501 (Line too long):** Allows long URLs, queries, and exploratory expressions without line-length warnings.

These exceptions support common notebook workflows but may also hide genuine issues.

### Magic and Terminal Commands

When `%clautofix` is enabled, automatic formatting is temporarily suppressed during the final execution of magic and terminal commands to prevent repeated formatting or linting.

To disable automatic formatting, run:

```python
%clautofix off
```
