import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def ensure_dependencies() -> None:
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import sqlmodel  # noqa: F401
    except Exception:
        req = os.path.join(ROOT, "requirements.txt")
        if sys.platform.startswith("linux"):
            cmd = [sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "--no-cache-dir", "-r", req]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", req]
        subprocess.check_call(cmd)


def main() -> None:
    ensure_dependencies()
    os.environ.setdefault("PYTHONPATH", ROOT)
    from backend.app import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()