try:
    from .magics import LintCellMagics, LintLineMagic

    def load_ipython_extension(ipython):
        ipython.register_magics(LintCellMagics)
        ipython.register_magics(LintLineMagic)
        print("[ColabLinter:INFO] cl commands registered.")

except Exception as e:
    print(f"[ColabLinter:ERROR] Initialization failed: {e}")
    pass
