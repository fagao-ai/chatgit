from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

import toml
from pydantic._internal._utils import deep_update
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource, InitSettingsSource, PydanticBaseSettingsSource
from pydantic_settings.sources import ENV_FILE_SENTINEL, DotEnvSettingsSource, DotenvType, SecretsSettingsSource

TomlEnvType = DotenvType


class MyBaseSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their order for loading the settings values.

        Args:
            settings_cls: The Settings class.
            init_settings: The `InitSettingsSource` instance.
            env_settings: The `EnvSettingsSource` instance.
            dotenv_settings: The `DotEnvSettingsSource` instance.
            file_secret_settings: The `SecretsSettingsSource` instance.

        Returns:
            A tuple containing the sources and their order for loading the settings values.
        """
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    def _settings_build_values(
        self,
        init_kwargs: dict[str, Any],
        _case_sensitive: bool | None = None,
        _env_prefix: str | None = None,
        _env_file: TomlEnvType | None = None,
        _env_file_encoding: str | None = None,
        _env_nested_delimiter: str | None = None,
        _secrets_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        # Determine settings config values
        case_sensitive = _case_sensitive if _case_sensitive is not None else self.model_config.get("case_sensitive")
        env_prefix = _env_prefix if _env_prefix is not None else self.model_config.get("env_prefix")
        env_file = _env_file if _env_file != ENV_FILE_SENTINEL else self.model_config.get("env_file")
        env_file_encoding = _env_file_encoding if _env_file_encoding is not None else self.model_config.get("env_file_encoding")
        env_nested_delimiter = _env_nested_delimiter if _env_nested_delimiter is not None else self.model_config.get("env_nested_delimiter")
        secrets_dir = _secrets_dir if _secrets_dir is not None else self.model_config.get("secrets_dir")

        # Configure built-in sources
        init_settings = InitSettingsSource(self.__class__, init_kwargs=init_kwargs)
        env_settings = EnvSettingsSource(
            self.__class__,
            case_sensitive=case_sensitive,
            env_prefix=env_prefix,
            env_nested_delimiter=env_nested_delimiter,
        )

        if env_file and Path(env_file).suffix == ".toml":
            env_file_settings = TomlSettingsSource(
                self.__class__,
                toml_file=env_file,
                toml_file_encoding=env_file_encoding,
                case_sensitive=case_sensitive,
                env_prefix=env_prefix,
                env_nested_delimiter=env_nested_delimiter,
            )
        else:
            env_file_settings = DotEnvSettingsSource(
                self.__class__,
                env_file=env_file,
                env_file_encoding=env_file_encoding,
                case_sensitive=case_sensitive,
                env_prefix=env_prefix,
                env_nested_delimiter=env_nested_delimiter,
            )

        file_secret_settings = SecretsSettingsSource(self.__class__, secrets_dir=secrets_dir, case_sensitive=case_sensitive, env_prefix=env_prefix)
        # Provide a hook to set built-in sources priority and add / remove sources
        sources = self.settings_customise_sources(
            self.__class__,
            init_settings=init_settings,
            env_settings=env_settings,
            dotenv_settings=env_file_settings,
            file_secret_settings=file_secret_settings,
        )
        if sources:
            return deep_update(*reversed([source() for source in sources]))
        else:
            # no one should mean to do this, but I think returning an empty dict is marginally preferable
            # to an informative error and much better than a confusing error
            return {}


class TomlSettingsSource(EnvSettingsSource):
    """
    A simple settings source class that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: TomlEnvType | None = ENV_FILE_SENTINEL,
        toml_file_encoding: str | None = None,
        case_sensitive: bool | None = None,
        env_prefix: str | None = None,
        env_nested_delimiter: str | None = None,
    ) -> None:
        self.env_file = toml_file if toml_file != ENV_FILE_SENTINEL else settings_cls.model_config.get("env_file")
        self.env_file_encoding = toml_file_encoding if toml_file_encoding is not None else settings_cls.model_config.get("env_file_encoding")
        super().__init__(settings_cls, case_sensitive, env_prefix, env_nested_delimiter)

    def _load_env_vars(self) -> Mapping[str, str | None]:
        return self._read_env_files(self.case_sensitive)

    def _read_env_files(self, case_sensitive: bool) -> Mapping[str, str | None]:
        env_files = self.env_file
        if env_files is None:
            return {}

        if isinstance(env_files, (str, os.PathLike)):
            env_files = [env_files]

        toml_env_vars: dict[str, str | None] = {}
        for env_file in env_files:
            env_path = Path(env_file).expanduser()
            if env_path.is_file():
                toml_env_vars.update(self._read_toml_env_file(env_path, case_sensitive=case_sensitive))

        return toml_env_vars

    def _read_toml_env_file(self, env_path: Path, case_sensitive):
        file_vars: dict[str, str | None] = toml.loads(env_path.read_text(encoding=self.env_file_encoding or "utf8"))
        if not case_sensitive:
            return {k.lower(): v for k, v in file_vars.items()}
        else:
            return file_vars

    def decode_complex_value(self, field_name: str, field: FieldInfo, value: Any) -> Any:
        """
        Decode the value for a complex field

        Args:
            field_name: The field name.
            field: The field.
            value: The value of the field that has to be prepared.

        Returns:
            The decoded value for further preparation
        """
        if isinstance(value, dict):
            return value
        return json.loads(value)

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = super().__call__()

        data_lower_keys: list[str] = []
        if not self.case_sensitive:
            data_lower_keys = [x.lower() for x in data.keys()]

        # As `extra` config is allowed in dotenv settings source, We have to
        # update data with extra env variabels from dotenv file.
        for env_name, env_value in self.env_vars.items():
            if env_name.startswith(self.env_prefix) and env_value is not None:
                env_name_without_prefix = env_name[self.env_prefix_len :]
                first_key, *_ = env_name_without_prefix.split(self.env_nested_delimiter)

                if (data_lower_keys and first_key not in data_lower_keys) or (not data_lower_keys and first_key not in data):
                    data[first_key] = env_value

        return data

    def __repr__(self) -> str:
        return (
            f"TomlEnvSettingsSource(env_file={self.env_file!r}, env_file_encoding={self.env_file_encoding!r}, "
            f"env_nested_delimiter={self.env_nested_delimiter!r}, env_prefix_len={self.env_prefix_len!r})"
        )
