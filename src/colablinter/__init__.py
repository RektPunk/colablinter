try:
    from .magics import LintMagics
    from .notebook import check_full as check_full

    def load_ipython_extension(ipython):
        ipython.register_magics(LintMagics)
        ipython.push({"check_full": check_full})

        print("[ColabLinter:INFO] %%format, %%check commands registered.")
        print("[ColabLinter:INFO] check_full() function loaded into namespace.")

except Exception as e:
    print(f"[ColabLinter:ERROR] Initialization failed: {e}")
    pass
