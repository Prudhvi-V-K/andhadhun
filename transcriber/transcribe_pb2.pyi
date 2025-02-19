from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AudioFile(_message.Message):
    __slots__ = ("filename", "format", "sample_rate", "channels", "audio_data")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    filename: str
    format: str
    sample_rate: int
    channels: int
    audio_data: bytes
    def __init__(self, filename: _Optional[str] = ..., format: _Optional[str] = ..., sample_rate: _Optional[int] = ..., channels: _Optional[int] = ..., audio_data: _Optional[bytes] = ...) -> None: ...

class HindiTranscribeResponse(_message.Message):
    __slots__ = ("status", "message", "original")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    status: str
    message: str
    original: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ..., original: _Optional[str] = ...) -> None: ...

class TranscribeResponse(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: str
    message: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
