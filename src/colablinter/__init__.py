try:
    from .magics import ColabLinterMagics, RequireDriveMountMagics

    def load_ipython_extension(ipython):
        ipython.register_magics(ColabLinterMagics)
        ipython.register_magics(RequireDriveMountMagics)
        print("[ColabLinter:INFO] cl commands registered.")

except Exception as e:
    print(f"[ColabLinter:ERROR] Initialization failed: {e}")
    pass
