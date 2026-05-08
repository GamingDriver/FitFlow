import os
import platform
import sys
import subprocess


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_shell():
    system = platform.system()
    shell = "unknown"

    if system == "Windows":
        # PowerShell
        if "PSModulePath" in os.environ:
            shell = "powershell"
            ''' find specific ps version
            if os.environ.get("POWERSHELL_DISTRIBUTION_CHANNEL"):
                shell = "powershell7"
            else:
                shell = "powershell5"
            '''
        # CMD
        elif os.environ.get("ComSpec", "").lower().endswith("cmd.exe"):
            shell = "cmd"

    elif system in ("Linux", "Darwin"):
        shell_path = os.environ.get("SHELL", "").lower()

        if "zsh" in shell_path:
            shell = "zsh"
        elif "bash" in shell_path:
            shell = "bash"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            shell = os.path.basename(shell_path) or "unix-shell"

    return {
        "os": system,
        "shell": shell,
        "python": sys.executable,
    }


def run(cmd, shell=False):
    # Run a command, streaming output live. Raises on non-zero exit
    print(f"  > {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}")


def install_requirements(py_exec):
    # Install dependencies
    req_path = os.path.join(SCRIPT_DIR, "..", "backend", "requirements.txt")
    run([py_exec, "-m", "pip", "install", "-r", req_path])


def start_server(py_exec):
    """Launch ../backend/main.py (blocking — runs until interrupted)."""
    server_path = os.path.join(SCRIPT_DIR, "..", "backend", "main.py")
    run([py_exec, server_path])


def main():
    sys_info = find_shell()
    print("=== System Info ===")
    for k, v in sys_info.items():
        print(f"  {k}: {v}")
    print()

    py_exec = sys_info["python"]

    print("=== Installing requirements ===")
    try:
        install_requirements(py_exec)
    except RuntimeError as e:
        print(f"[ERROR] Failed to install requirements: {e}")
        sys.exit(1)

    print()
    print("=== Starting server ===")
    try:
        start_server(py_exec)
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    except RuntimeError as e:
        print(f"[ERROR] Server exited unexpectedly: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()