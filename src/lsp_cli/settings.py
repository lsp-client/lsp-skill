from pathlib import Path
from typing import Final, Literal

from platformdirs import user_config_dir, user_log_dir, user_runtime_dir
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

APP_NAME = "lsp-cli"
CONFIG_PATH = Path(user_config_dir(APP_NAME)) / "config.toml"
RUNTIME_DIR = Path(user_runtime_dir(APP_NAME))
LOG_DIR = Path(user_log_dir(APP_NAME))
MANAGER_LOG_PATH = LOG_DIR / "manager.log"
CLIENT_LOG_DIR = LOG_DIR / "clients"
MANAGER_UDS_PATH = RUNTIME_DIR / "manager.sock"

LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    idle_timeout: int = 600
    log_level: LogLevel = "INFO"

    # UX improvements
    default_max_items: int | None = 20
    model_config = SettingsConfigDict(
        env_prefix="LSP_",
        toml_file=CONFIG_PATH,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )


settings: Final = Settings()
