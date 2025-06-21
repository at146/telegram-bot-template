from typing import Annotated, Literal

from pydantic import (
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    NoDecode,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    # .env
    ENVIRONMENT: Literal["local", "production"]

    # TELEGRAM: Telegram
    BOT_TOKEN: str
    USE_WEBHOOK: bool
    RESET_WEBHOOK: bool
    DROP_PENDING_UPDATES: bool

    MAIN_WEBHOOK_ADDRESS: str
    MAIN_BOT_PATH: str
    MAIN_WEBHOOK_SECRET_TOKEN: str
    MAIN_WEBHOOK_LISTENING_HOST: str
    MAIN_WEBHOOK_LISTENING_PORT: int

    BOT_ADMINS_IDS: Annotated[list[int], NoDecode]

    @field_validator("BOT_ADMINS_IDS", mode="before")
    @classmethod
    def list_bot_admins_ids(cls, v: str) -> list[int]:
        return [int(x) for x in v.split(",")]

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
            env_settings,
            dotenv_settings,
        )


settings = Settings()  # type: ignore
