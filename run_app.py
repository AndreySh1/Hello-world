import os
import sys
import subprocess
from typing import Tuple

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


def parse_host_port(argv: list) -> Tuple[str, int]:
	host = os.getenv("HOST", "0.0.0.0")
	port_env = os.getenv("PORT", "8000")
	try:
		port = int(port_env)
	except Exception:
		port = 8000
	# simple cli parsing: --host X --port Y
	for i, tok in enumerate(argv):
		if tok == "--host" and i + 1 < len(argv):
			host = argv[i + 1]
		if tok == "--port" and i + 1 < len(argv):
			try:
				port = int(argv[i + 1])
			except Exception:
				pass
	return host, port


def main() -> None:
	ensure_dependencies()
	os.environ.setdefault("PYTHONPATH", ROOT)
	host, port = parse_host_port(sys.argv[1:])
	from backend.app import app
	import uvicorn
	uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
	main()