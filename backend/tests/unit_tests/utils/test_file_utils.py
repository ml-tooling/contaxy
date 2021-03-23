import asyncio
import os
import threading
from typing import AsyncGenerator

import pytest

from contaxy.utils.file_utils import FormMultipartStream, SyncFromAsyncGenerator

from ..managers.file.data.metadata import file_data


@pytest.mark.unit
class TestFormMultipartStream:
    @pytest.mark.parametrize("metadata", file_data)
    def test_multipart_stream(self, metadata: dict) -> None:
        with open(str(metadata.get("file_path")), "rb") as file_stream:
            multipart_stream = FormMultipartStream(
                file_stream, metadata.get("headers"), hash_algo="md5"
            )

            assert multipart_stream.filename == metadata.get("filename")
            assert multipart_stream.content_type == metadata.get("content_type")

            with open(os.devnull, "wb") as file:
                while True:
                    chunk = multipart_stream.read(10 * 1024)
                    if not chunk:
                        break
                    file.write(chunk)

            assert multipart_stream.hash == metadata.get("hash")


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
