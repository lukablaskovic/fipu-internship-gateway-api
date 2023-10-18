from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: int
    db_password: str
    db_name: str
    db_username: str
    secret_key: str
    algorithm: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REMEMBER_ME_EXPIRE_MINUTES: int
    BUGSNAG: str
    BASEROW_CONNECTOR_URL: str
    BPMN_ENGINE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
