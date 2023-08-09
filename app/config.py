from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: int
    db_password: str
    db_name: str
    db_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
