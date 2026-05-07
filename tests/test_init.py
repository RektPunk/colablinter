from IPython.core.interactiveshell import InteractiveShell

from colablinter import load_ipython_extension


def test_load_ipython_extension(monkeypatch):
    shell = InteractiveShell()
    registered = False
    clautofix_called = False

    def mock_register_magics(magics_class):
        nonlocal registered
        registered = True

    def mock_run_line_magic(name, value):
        nonlocal clautofix_called
        if name == "clautofix" and value == "on":
            clautofix_called = True

    monkeypatch.setattr(shell, "register_magics", mock_register_magics)
    monkeypatch.setattr(shell, "run_line_magic", mock_run_line_magic)

    load_ipython_extension(shell)
    assert registered
    assert clautofix_called
