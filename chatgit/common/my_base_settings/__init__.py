import pydantic

pydantic_version = pydantic.__version__
if pydantic_version >= "2.0.0":
    from chatgit.common.my_base_settings.base_settings_v2 import MyBaseSettings
else:
    from chatgit.common.my_base_settings.base_settings_v1 import MyBaseSettings

__all__ = ["MyBaseSettings"]
