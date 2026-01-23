from typing import Final

from attrs import define
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvState(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LSP_")

    debug: bool = False
    "Enable verbose debug logging for troubleshooting."


env_state: Final = EnvState()


@define
class RuntimeState:
    client_id: str | None = None
    "The current active client ID."
