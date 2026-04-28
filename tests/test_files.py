import asyncio

import pytest

from blog_generator.files import is_supported_text_file, read_upload_text


class FakeUpload:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content


def test_supported_text_extensions() -> None:
    assert is_supported_text_file("notes.md")
    assert is_supported_text_file("data.csv")
    assert not is_supported_text_file("report.pdf")


def test_read_upload_text_truncates_content() -> None:
    upload = FakeUpload(filename="notes.txt", content=b"abcdef")

    assert asyncio.run(read_upload_text(upload, max_chars=3)) == "abc"


def test_read_upload_text_rejects_binary_extension() -> None:
    upload = FakeUpload(filename="image.png", content=b"abc")

    with pytest.raises(ValueError):
        asyncio.run(read_upload_text(upload, max_chars=100))
