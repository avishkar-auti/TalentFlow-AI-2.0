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
