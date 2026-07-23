import sys
import os
from pathlib import Path

# Ensure project root is in sys.path and PYTHONPATH so child reloader subprocesses inherit it
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

existing_pythonpath = os.environ.get("PYTHONPATH", "")
if str(ROOT_DIR) not in existing_pythonpath:
    os.environ["PYTHONPATH"] = f"{ROOT_DIR};{existing_pythonpath}" if existing_pythonpath else str(ROOT_DIR)

import uvicorn
from backend.config import settings

def main() -> None:
    """Main entrypoint for running the Uvicorn server."""
    uvicorn.run(
        "backend.app:create_app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        factory=True,
    )

if __name__ == "__main__":
    main()


