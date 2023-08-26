from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import AbstractSet, Any, ClassVar, Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseConfig, BaseSettings, Extra
from pydantic.env_settings import (
    DotenvType,
    EnvSettingsSource,
    InitSettingsSource,
    SecretsSettingsSource,
    SettingsSourceCallable,
    env_file_sentinel,
)
from pydantic.fields import ModelField
from pydantic.typing import StrPath, display_as_type
from pydantic.utils import deep_update, sequence_like


class MyBaseSettings(BaseSettings):
    def _build_values(
        self,
        init_kwargs: Dict[str, Any],
        _env_file: Optional[DotenvType] = None,
        _env_file_encoding: Optional[str] = None,
        _env_nested_delimiter: Optional[str] = None,
        _secrets_dir: Optional[StrPath] = None,
    ) -> Dict[str, Any]:
        # Configure built-in sources
        init_settings = InitSettingsSource(init_kwargs=init_kwargs)
        env_settings = MyEnvSettingsSource(
            env_file=(_env_file if _env_file != env_file_sentinel else self.__config__.env_file),
            env_file_encoding=(_env_file_encoding if _env_file_encoding is not None else self.__config__.env_file_encoding),
            env_nested_delimiter=(_env_nested_delimiter if _env_nested_delimiter is not None else self.__config__.env_nested_delimiter),
            env_prefix_len=len(self.__config__.env_prefix),
        )
        file_secret_settings = SecretsSettingsSource(secrets_dir=_secrets_dir or self.__config__.secrets_dir)
        # Provide a hook to set built-in sources priority and add / remove sources
        sources = self.__config__.customise_sources(init_settings=init_settings, env_settings=env_settings, file_secret_settings=file_secret_settings)
        if sources:
            return deep_update(*reversed([source(self) for source in sources]))
        else:
            # no one should mean to do this, but I think returning an empty dict is marginally preferable
            # to an informative error and much better than a confusing error
            return {}

    class Config(BaseConfig):
        env_prefix: str = ""
        env_file: Optional[DotenvType] = None
        env_file_encoding: Optional[str] = None
        env_nested_delimiter: Optional[str] = None
        secrets_dir: Optional[StrPath] = None
        validate_all: bool = True
        extra: Extra = Extra.forbid
        arbitrary_types_allowed: bool = True
        case_sensitive: bool = False

        @classmethod
        def prepare_field(cls, field: ModelField) -> None:
            env_names: Union[List[str], AbstractSet[str]]
            field_info_from_config = cls.get_field_info(field.name)

            env = field_info_from_config.get("env") or field.field_info.extra.get("env")
            if env is None:
                if field.has_alias:
                    warnings.warn(
                        "aliases are no longer used by BaseSettings to define which environment variables to read. "
                        'Instead use the "env" field setting. '
                        "See https://pydantic-docs.helpmanual.io/usage/settings/#environment-variable-names",
                        FutureWarning,
                        stacklevel=2,
                    )
                env_names = {cls.env_prefix + field.name}
            elif isinstance(env, str):
                env_names = {env}
            elif isinstance(env, (set, frozenset)):
                env_names = env
            elif sequence_like(env):
                env_names = list(env)
            else:
                raise TypeError(f"invalid field env: {env!r} ({display_as_type(env)}); should be string, list or set")

            if not cls.case_sensitive:
                env_names = env_names.__class__(n.lower() for n in env_names)
            field.field_info.extra["env_names"] = env_names

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, file_secret_settings

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: Union[str, Dict[str, Any]]) -> Any:
            if isinstance(raw_val, str):
                return cls.json_loads(raw_val)
            else:
                return raw_val

    # populated by the metaclass using the Config class defined above, annotated here to help IDEs only.
    __config__: ClassVar[Type[Config]]  # type: ignore


def read_env_file(file_path: StrPath, *, encoding: str | None = None, case_sensitive: bool = False) -> Dict[str, Optional[str]]:
    file_pure_path = Path(file_path)
    file_path_suffix = file_pure_path.suffix
    if file_path_suffix == ".toml":
        try:
            import toml
        except ImportError as e:
            raise ImportError("toml is not installed, run `pip install toml`") from e
        file_vars: dict[str, str | None] = toml.loads(file_pure_path.read_text(encoding=encoding or "utf8"))
    else:
        try:
            from dotenv import dotenv_values
        except ImportError as e:
            raise ImportError("python-dotenv is not installed, run `pip install pydantic[dotenv]`") from e

        file_vars: Dict[str, Optional[str]] = dotenv_values(file_path, encoding=encoding or "utf8")  # type: ignore
    if not case_sensitive:
        return {k.lower(): v for k, v in file_vars.items()}
    else:
        return file_vars


class MyEnvSettingsSource(EnvSettingsSource):
    def _read_env_files(self, case_sensitive: bool) -> Dict[str, Optional[str]]:
        env_files = self.env_file
        if env_files is None:
            return {}

        if isinstance(env_files, (str, os.PathLike)):
            env_files = [env_files]

        dotenv_vars = {}
        for env_file in env_files:
            env_path = Path(env_file).expanduser()
            if env_path.is_file():
                dotenv_vars.update(read_env_file(env_path, encoding=self.env_file_encoding, case_sensitive=case_sensitive))

        return dotenv_vars
