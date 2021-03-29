import asyncio
import io
import os
import threading
from typing import AsyncGenerator

import pytest

from contaxy.utils.file_utils import (
    FileStreamWrapper,
    FormMultipartStream,
    SyncFromAsyncGenerator,
)


@pytest.fixture()
def metadata() -> dict:
    return {
        "filename": "test.csv",
        "headers": {
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryr1D8WqBUjhPTDqlM"
        },
        "hash": "8fec240e6375b677643833f672cfbc5c",
        "content_type": "text/csv",
    }


@pytest.fixture()
def multipart_data(metadata: dict) -> dict:

    stream = b'------WebKitFormBoundaryr1D8WqBUjhPTDqlM\r\nContent-Disposition: form-data; name="file"; filename="test.csv"\r\nContent-Type: text/csv\r\n\r\n'
    stream += 5000 * b"foo;bar\n"
    stream += b"\r\n------WebKitFormBoundaryr1D8WqBUjhPTDqlM--\r\n"

    metadata.update({"stream": io.BytesIO(stream)})

    return metadata


@pytest.fixture()
def file_data(metadata: dict) -> dict:
    metadata.update({"stream": io.BytesIO(5000 * b"foo;bar\n")})
    return metadata


@pytest.mark.unit
class TestFormMultipartStream:
    def test_multipart_stream(self, multipart_data: dict) -> None:

        file_stream = multipart_data.get("stream")
        assert file_stream

        multipart_stream = FormMultipartStream(
            file_stream, multipart_data.get("headers"), hash_algo="md5"
        )

        assert multipart_stream.filename == multipart_data.get("filename")
        assert multipart_stream.content_type == multipart_data.get("content_type")

        with open(os.devnull, "wb") as file:
            while True:
                chunk = multipart_stream.read(10 * 1024)
                if not chunk:
                    break
                file.write(chunk)

        assert multipart_stream.hash == multipart_data.get("hash")


@pytest.mark.unit
class TestSyncFromAsyncGenerator:
    def test_iteration(self) -> None:

        data = list(range(5))

        async def iterate(data: list) -> AsyncGenerator:
            for element in data:
                yield element

        async_generator = iterate(data)

        loop = asyncio.new_event_loop()
        t = threading.Thread(target=loop.run_forever, daemon=True)
        t.start()

        sync_generator = SyncFromAsyncGenerator(async_generator, loop)

        iterated_data = [element for element in sync_generator]
        loop.stop()
        assert data == iterated_data


@pytest.mark.unit
class TestFileStreamWrapper:
    def test_file_stream_wrapper(self, file_data: dict) -> None:

        wrapped_file_stream = FileStreamWrapper(file_data.get("stream"))
        initial_hash = wrapped_file_stream.hash

        while True:
            chunk = wrapped_file_stream.read(10 * 1024)
            if not chunk:
                break

        assert initial_hash != wrapped_file_stream.hash
        assert wrapped_file_stream.hash == file_data.get("hash")
