from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_name: str = 'EDMS'
    app_env: str = 'development'
    debug: bool = False
    secret_key: str

    database_url: str
    test_database_url: str

    redis_url: str
    redis_cache_ttl: int = 300

    celery_broker_url: str
    celery_result_backend: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    @property
    def refresh_token_expire_minutes(self) -> int:
        return self.refresh_token_expire_days * 24 * 60

    @property
    def refresh_cookie_max_age(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str
    minio_secure: bool = False

    cors_origins: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()