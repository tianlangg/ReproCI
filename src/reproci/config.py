from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REPROCI_")
    database_url: str = "postgresql+psycopg://reproci:reproci@localhost:5432/reproci"
    artifact_root: str = "/artifacts"
    artifact_volume: str = "reproci_artifacts"
    max_concurrent_jobs: int = 2
    attempt_timeout: int = 120
    github_secret: str = ""
    api_url: str = "http://127.0.0.1:8001"
    max_log_bytes: int = 5 * 1024 * 1024


settings = Settings()
