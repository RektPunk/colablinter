import os
import unicodedata
import urllib.parse

import ipykernel
import requests

from .utils import execute_command

_BASE_PATH = "/content/drive"


def _colab_drive_mount() -> None:
    try:
        from google.colab import drive

        if not os.path.exists(_BASE_PATH):
            print("[ColabLinter:INFO] Mounting Google Drive required.")
            drive.mount(_BASE_PATH)
    except ImportError:
        raise ImportError(
            "This command requires the 'google.colab' environment.\n"
            "The `colablinter` must be run **inside a Google Colab notebook** to access the kernel and Drive.\n"
            "If you are already in Colab, ensure you haven't renamed the `google.colab` package or run the command outside a code cell."
        )


def _get_notebook_filename() -> str | None:
    print("[ColabLinter:INFO] Searching matched filename in kernel and session.")
    try:
        connection_file = ipykernel.get_connection_file()
        kernel_id = (
            os.path.basename(connection_file)
            .removeprefix("kernel-")
            .removesuffix(".json")
        )
    except Exception as e:
        kernel_id = None
        print(f"[ColabLinter:WARNING] Failed to retrieve kernel ID: {e}")
        pass

    try:
        colab_ip = execute_command("hostname -I", "")
        if colab_ip is None:
            raise RuntimeError("Failed to get Colab instance IP address.")

        colab_ip = colab_ip.split()[0].strip()
        api_url = f"http://{colab_ip}:9000/api/sessions"

        response = requests.get(api_url, timeout=5)
        if response.status_code != 200:
            response.raise_for_status()
            raise requests.exceptions.HTTPError(
                f"API Unexpected HTTP Error {response.status_code}: {response.reason}"
            )
        sessions: list[dict] = response.json()
        if sessions is None:
            raise RuntimeError("Failed to get Colab instance sessions.")

        if kernel_id:
            for session in sessions:
                if session.get("kernel", {}).get("id") == kernel_id:
                    print(
                        f"[ColabLinter:INFO] Kernel ID ({kernel_id}) matched with session."
                    )
                    encoded_filename = session.get("name")
                    return urllib.parse.unquote(encoded_filename)

        encoded_filename = sessions[0].get("name")
        if encoded_filename:
            return urllib.parse.unquote(encoded_filename)
        return

    except requests.exceptions.Timeout:
        raise requests.exceptions.Timeout(f"API request timed out: {api_url}")
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"API HTTP Error {e.response.status_code}: {e.response.reason}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to connect to API: {e}")
    except Exception:
        return


def _find_notebook_path(filename: str) -> str | None:
    print(
        "[ColabLinter:INFO] Searching file path in Google Drive. (This may take time...)"
    )
    normalized_filename = unicodedata.normalize("NFC", filename)
    for root, _, files in os.walk(_BASE_PATH):
        for file in files:
            normalized_file = unicodedata.normalize("NFC", file)
            if normalized_filename == normalized_file:
                return os.path.join(root, file)
        if filename in files:
            return os.path.join(root, filename)
    return


def _check_entire_notebook(notebook_path: str) -> None:
    print("---- Notebook Quality & Style Check Report ----")
    try:
        report = execute_command(
            f"ruff check '{notebook_path}'",
            "",
        )
        if report:
            print(report)
        else:
            print(
                "[ColabLinter:INFO] No issues found in the entire notebook. Code is clean."
            )
    except FileNotFoundError:
        raise FileNotFoundError(f"File not founded: {notebook_path}.")
    except Exception as e:
        raise RuntimeError(f"%cl_check failed: {e}")
    print("-------------------------------------------------------------")


class ColabLinter:
    __instance = None
    _notebook_filename_cache: str | None = None
    _notebook_path_cache: str | None = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if ColabLinter._notebook_path_cache:
            return

        _colab_drive_mount()

        ColabLinter._notebook_filename_cache = _get_notebook_filename()
        self.__check_notebook_filename_exists()

        ColabLinter._notebook_path_cache = _find_notebook_path(self.notebook_filename)
        self.__check_notebook_path_exists()

    def check(self) -> None:
        _check_entire_notebook(self.notebook_path)

    @property
    def notebook_filename(self) -> str:
        if ColabLinter._notebook_filename_cache is None:
            raise ValueError("Notebook filename has not been initialized.")
        return ColabLinter._notebook_filename_cache

    def __check_notebook_filename_exists(self) -> None:
        if self.notebook_filename is None:
            raise ValueError(
                "Could not retrieve current filename. Check if the file is saved."
            )
        print(
            f"[ColabLinter:INFO] Notebook filename detected: {self.notebook_filename}"
        )

    @property
    def notebook_path(self) -> str:
        if ColabLinter._notebook_path_cache is None:
            raise ValueError("Notebook path has not been initialized.")
        return ColabLinter._notebook_path_cache

    def __check_notebook_path_exists(self) -> None:
        if self.notebook_path is None:
            raise ValueError(
                f"File not found in Google Drive. Ensure the notebook is in '{_BASE_PATH}'."
            )
        print(f"[ColabLinter:INFO] File path found: {self.notebook_path}")
