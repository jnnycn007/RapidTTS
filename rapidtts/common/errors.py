# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
class RapidTTSError(Exception):
    pass


class InvalidRequestError(RapidTTSError):
    pass


class ConfigError(RapidTTSError):
    pass


class BackendNotLoadedError(RapidTTSError):
    pass


class UnsupportedModelError(RapidTTSError):
    pass


class AudioEncodeError(RapidTTSError):
    pass
