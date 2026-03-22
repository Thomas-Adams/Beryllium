from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "beryl"
    db_user: str = "beryl_admin"
    db_password: str = "beryl_admin"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    app_name: str = "Beryl CMS"
    debug: bool = True

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_prefix = "BERYL_"
        env_file = ".env"


# Singleton instance — imported everywhere
settings = Settings()