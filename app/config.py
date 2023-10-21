from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOSTNAME: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_DB_NAME: str
    POSTGRES_USERNAME: str
    SECRET_KEY: str
    PASS_HASHING_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REMEMBER_ME_EXPIRE_MINUTES: int
    BUGSNAG: str
    BASEROW_CONNECTOR_URL: str
    BPMN_ENGINE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
