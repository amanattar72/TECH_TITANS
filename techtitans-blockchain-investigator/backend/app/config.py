from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"
    etherscan_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
