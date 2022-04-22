import asyncio
import hashlib
from collections.abc import AsyncGenerator, Generator
from hashlib import sha1
from typing import Any, Callable, Mapping, Optional

import filetype
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import BaseTarget

from contaxy.schema.file import FileStream


class MultipartStreamTarget(BaseTarget):
    """StreamTarget stores one chunk at a time in-memory and deletes it upon read.

    This is useful in case you'd like to have a parsed stream.
    """

    def __init__(
        self, validator: Optional[Callable] = None, hash_algo: Optional[str] = "md5"
    ) -> None:
        super().__init__(validator)

        self._chunk = b""
        self._hash = hashlib.new(hash_algo) if hash_algo else None

    def on_data_received(self, chunk: bytes) -> None:
        self._chunk = chunk
        if self._hash:
            self._hash.update(self._chunk)

    @property
    def value(self) -> bytes:
        chunk = self._chunk
        self._chunk = b""
        return chunk

    @property
    def hash(self) -> str:
        # Todo: Throw error
        if not self._hash:
            raise ValueError("No hash algorithm was set during object intialization")
        return self._hash.hexdigest()


class FormMultipartStream(FileStream):
    def __init__(
        self,
        stream: Generator,
        headers: Mapping[str, str],
        form_field: str = "file",
        pre_read_size: int = 1024,
        hash_algo: Optional[str] = "md5",
    ) -> None:
        """Currently, it is a requirement that the multipart/form-data stream embodies only one form field, i.e. the form_field parameter.

        Args:
            stream (Generator): The multipart/form-data byte stream.
            headers (Mapping[str, str]): Http header of the reuqest.
            form_field (str, optional): The name of the form field used to upload the file. Defaults to "file".
            pre_read_size (int): The pre_read_size controls the byte size which will be used to determine some metadata in advance e.g. a filename based on the content-disposition. Defaults to 1024.
            hash_algo (Optional[str]): Name of the hash algorithm supported by python's hashlib. If not set, now file hash will be calculated.
        """
        self._stream = stream
        self._parser = StreamingFormDataParser(headers=headers)
        self._stream_target = MultipartStreamTarget(hash_algo=hash_algo)
        self._parser.register(form_field, self._stream_target)
        self.is_stream_finished = False
        self._unprocessed_bytes = b""
        # This will try to parse the metadata from the beginning of the stream
        self._unprocessed_bytes = self.read(pre_read_size) + self._unprocessed_bytes
        # Try guess mime type based on magic numbers
        self._guessed_content_type = filetype.guess_mime(self._unprocessed_bytes)

    @property
    def filename(self) -> Optional[str]:
        return self._stream_target.multipart_filename

    @property
    def content_type(self) -> Optional[str]:
        default_mime = "application/octet-stream"
        if (
            self._stream_target.multipart_content_type
            and self._stream_target.multipart_content_type != default_mime
        ):
            return self._stream_target.multipart_content_type
        elif self._guessed_content_type:
            return self._guessed_content_type
        else:
            return default_mime

    @property
    def hash(self) -> str:
        try:
            return self._stream_target.hash
        except ValueError:
            return ""

    def read(self, size: int = -1) -> bytes:

        if size == 0:
            return b""

        unprocessed_bytes_length = len(self._unprocessed_bytes)

        while (
            unprocessed_bytes_length < size or size == -1
        ) and not self.is_stream_finished:
            try:
                raw_chunk = self._stream.__next__()
            except StopIteration:
                self.is_stream_finished = True
                break

            self._parser.data_received(raw_chunk)
            parsed_chunk = self._stream_target.value
            self._unprocessed_bytes += parsed_chunk
            unprocessed_bytes_length = len(self._unprocessed_bytes)

        if unprocessed_bytes_length > size and size > -1:
            required_bytes = max(size - unprocessed_bytes_length, size)
            bytes_received = self._unprocessed_bytes[:required_bytes]
            self._unprocessed_bytes = self._unprocessed_bytes[required_bytes:]
        else:
            bytes_received = self._unprocessed_bytes
            self._unprocessed_bytes = b""

        return bytes_received


class SyncFromAsyncGenerator(Generator):
    """This genrator implementation wraps an async generator to make it compatible for sync implementations."""

    def __init__(
        self,
        async_generator: AsyncGenerator,
        event_loop: asyncio.AbstractEventLoop,
    ) -> None:
        super().__init__()
        self._generator = async_generator
        self._event_loop = event_loop

    def __next__(self) -> Any:
        try:
            data = asyncio.run_coroutine_threadsafe(
                self._generator.__anext__(), self._event_loop
            ).result()
            return data
        except StopAsyncIteration:
            raise StopIteration()

    def send(self, value) -> Any:  # type: ignore
        data = asyncio.run_coroutine_threadsafe(
            self._generator.asend(value), self._event_loop
        ).result()
        return data

    def throw(self, typ, val=None, tb=None) -> None:  # type: ignore
        asyncio.run_coroutine_threadsafe(
            self._generator.athrow(typ, val, tb), self._event_loop
        )

    def close(self) -> None:
        asyncio.run_coroutine_threadsafe(self._generator.aclose(), self._event_loop)

    def __iter__(self) -> Generator:
        return self


def generate_file_id(file_name: str, version_id: str) -> str:
    return sha1(bytes(f"{file_name}{version_id}", "utf8")).hexdigest()
