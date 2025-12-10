try:
    from .magics import LintMagics

    def load_ipython_extension(ipython):
        ipython.register_magics(LintMagics)

        print("[ColabLinter:INFO] %%format, %%check commands registered.")
        print("[ColabLinter:INFO] check_full() function loaded into namespace.")

except Exception as e:
    print(f"[ColabLinter:ERROR] Initialization failed: {e}")
    pass
