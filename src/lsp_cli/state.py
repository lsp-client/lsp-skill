from pydantic_settings import BaseSettings, SettingsConfigDict


class State(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LSP_")

    debug: bool = False
    "Enable verbose debug logging for troubleshooting."


state = State()
