import os

import ipykernel
import requests

from .utils import execute_command

_BASE_PATH = "/content/drive"


def _get_notebook_filename() -> str | None:
    try:
        connection_file = ipykernel.get_connection_file()
        kernel_id = (
            os.path.basename(connection_file)
            .removeprefix("kernel-")
            .removesuffix(".json")
        )
    except Exception:
        kernel_id = None
        pass

    try:
        colab_ip = execute_command("hostname -I", "")
        if colab_ip is None:
            raise Exception

        colab_ip = colab_ip.split()[0].strip()
        api_url = f"http://{colab_ip}:9000/api/sessions"

        response = requests.get(api_url, timeout=5)
        response.raise_for_status()

        if response.status_code == 200:
            sessions: list[dict] = response.json()
            if sessions is None:
                return

            if kernel_id:
                for session in sessions:
                    if session.get("kernel", {}).get("id") == kernel_id:
                        print(f"[ColabLinter:INFO] Kernel ID ({kernel_id}) matched.")
                        return session.get("name")
            return sessions[0].get("name")
    except Exception:
        return


def _find_notebook_path(filename: str) -> str | None:
    for root, _, files in os.walk(_BASE_PATH):
        if filename in files:
            return os.path.join(root, filename)
    return


def _check_entire_notebook(notebook_path: str) -> None:
    print("---- Notebook Quality & Style Check Report ----")
    try:
        report = execute_command(
            f"ruff check {notebook_path}",
            "",
        )
        if report:
            print(report)
        else:
            print(
                "[ColabLinter:INFO] No issues found in the entire notebook. Code is clean."
            )
    except FileNotFoundError:
        print(f"[ColabLinter:ERROR] File not founded: {notebook_path}.")
    except Exception as e:
        print(f"[ColabLinter:ERROR] Check full failed: {e}")
    print("-------------------------------------------------------------")


def check_full():
    try:
        from google.colab import drive

        if not os.path.exists(_BASE_PATH):
            print("[ColabLinter:INFO] Mounting Google Drive required.")
            drive.mount(_BASE_PATH)
    except ImportError:
        print("[ColabLinter:ERROR] Not a Colab environment (google.colab not found).")
        return

    notebook_filename = _get_notebook_filename()
    if notebook_filename is None:
        print(
            "[ColabLinter:WARN] Could not retrieve current notebook filename. Check if the file is saved."
        )
        return

    print(f"[ColabLinter:INFO] Notebook filename detected: {notebook_filename}")
    print(
        "[ColabLinter:INFO] Searching file path in Google Drive. (This may take time...)"
    )
    notebook_path = _find_notebook_path(notebook_filename)

    if notebook_path:
        print(f"[ColabLinter:INFO] File path found: {notebook_path}")
        _check_entire_notebook(notebook_path)
    else:
        print(
            "[ColabLinter:ERROR] File not found in Google Drive. Ensure the notebook is in 'My Drive'."
        )
