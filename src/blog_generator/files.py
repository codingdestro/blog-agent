from pathlib import Path

from fastapi import UploadFile

TEXT_EXTENSIONS = {
    ".csv",
    ".json",
    ".log",
    ".md",
    ".rst",
    ".text",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def is_supported_text_file(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in TEXT_EXTENSIONS or not suffix


async def read_upload_text(upload: UploadFile, max_chars: int) -> str:
    if not is_supported_text_file(upload.filename or ""):
        raise ValueError(f"{upload.filename} is not a supported text file")

    raw = await upload.read()
    text = raw.decode("utf-8", errors="replace").strip()
    return text[:max_chars]

