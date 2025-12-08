try:
    from .magics import LintMagics

    def load_ipython_extension(ipython):
        ipython.register_magics(LintMagics)
        print("[ColabLinter:INFO] %%format, %%check commands registered.")

except Exception as e:
    print(f"[ColabLinter:ERROR] Initialization failed: {e}")
    pass
