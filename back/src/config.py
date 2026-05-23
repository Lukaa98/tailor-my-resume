from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

# Get the project root (back/)
ROOT_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8081
    
    class Config:
        env_file = str(ROOT_DIR / ".env")
        case_sensitive = False

    @property
    def frontend_origins(self) -> list[str]:
        origins: list[str] = []

        for raw_value in self.frontend_url.split(","):
            candidate = raw_value.strip()
            if not candidate:
                continue

            parsed = urlparse(candidate)
            if parsed.scheme and parsed.netloc:
                origins.append(f"{parsed.scheme}://{parsed.netloc}")
            else:
                origins.append(candidate.rstrip("/"))

        return list(dict.fromkeys(origins))

@lru_cache()
def get_settings():
    return Settings()
