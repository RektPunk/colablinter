import pytest
from IPython.core.interactiveshell import ExecutionInfo, InteractiveShell

from colablinter.magics import ColabLinterMagics


@pytest.fixture
def shell():
    return InteractiveShell()


@pytest.fixture
def magics(shell):
    return ColabLinterMagics(shell=shell)


def test_clcheck_integration(magics, monkeypatch):
    cells_run = []
    monkeypatch.setattr(
        magics.shell, "run_cell", lambda cell, **kwargs: cells_run.append(cell)
    )

    logs = []
    monkeypatch.setattr("colablinter.magics.logger.info", lambda msg: logs.append(msg))

    magics.clcheck("", "f'test'")

    assert any("F541" in log for log in logs)
    assert "f'test'" in cells_run


def test_clunsafefix_integration(magics, monkeypatch):
    cells_run = []
    monkeypatch.setattr(
        magics.shell, "run_cell", lambda cell, **kwargs: cells_run.append(cell)
    )

    next_inputs = []
    monkeypatch.setattr(
        magics.shell, "set_next_input", lambda code, replace: next_inputs.append(code)
    )

    magics.clunsafefix("", "x is 'a'")

    assert len(cells_run) == 1
    assert "x == 'a'" in cells_run[0]
    assert "x == 'a'" in next_inputs[0]


def test_clautofix_toggle(magics, monkeypatch):
    magics.clautofix("off")
    assert magics._is_autofix_active is False

    magics.clautofix("on")
    assert magics._is_autofix_active is True


def test_autofix_event_integration(magics, monkeypatch):
    next_inputs = []
    monkeypatch.setattr(
        magics.shell, "set_next_input", lambda code, replace: next_inputs.append(code)
    )

    magics.clautofix("on")
    info = ExecutionInfo("x=1+2", False, False, True, "cell_id")
    magics._ColabLinterMagics__autofix(info)

    assert len(next_inputs) == 1
    assert "x = 1 + 2" in next_inputs[0]
