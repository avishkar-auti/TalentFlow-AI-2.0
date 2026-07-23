from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Server
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Firebase
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_storage_bucket: str = "talentflow-ai.appspot.com"
    
    # LLM API Keys
    gemini_api_key: str = ""
    groq_api_key: str = ""
    
    # LLM Provider routing
    resume_llm_provider: str = "groq"
    matching_llm_provider: str = "groq"
    decision_llm_provider: str = "groq"
    interview_llm_provider: str = "gemini"
    
    # Upload
    max_upload_size_mb: int = 10
    
    # Interview
    interview_max_duration_minutes: int = 45
    interview_context_window_turns: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
