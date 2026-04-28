from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import generate_blog, upload_blog
from .config import get_settings
from .db import get_blog, init_db, list_all_blogs, list_blogs, save_blog
from .files import read_upload_text
from .models import BlogRequest, UploadedSource

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="Blog Generator", version="0.1.0")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.on_event("startup")
    async def startup() -> None:
        init_db(get_settings().database_path)

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/index.html")
    async def index_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/generator.html")
    async def generator_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "generator.html")

    @app.get("/blog.html")
    async def blog_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "blog.html")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/blogs")
    async def blogs() -> list[dict]:
        return list_all_blogs(get_settings().database_path)

    @app.get("/api/blogs/summaries")
    async def blog_summaries() -> list[dict]:
        return list_blogs(get_settings().database_path)

    @app.get("/api/blogs/{blog_id}")
    async def blog(blog_id: int) -> dict:
        stored_blog = get_blog(get_settings().database_path, blog_id)
        if stored_blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        return stored_blog

    @app.get("/api/publish/{blog_id}")
    async def publish_blog(blog_id:int) ->dict:
        settings = get_settings()
        return upload_blog(blog_id,settings)

    @app.post("/api/generate")
    async def generate(
        topic: Annotated[str, Form()],
        tone: Annotated[str, Form()] = "clear, useful, and professional",
        audience: Annotated[str, Form()] = "general readers",
        word_count: Annotated[int, Form()] = 900,
        files: Annotated[list[UploadFile] | None, File()] = None,
    ) -> dict:
        settings = get_settings()
        uploaded_sources: list[UploadedSource] = []

        for upload in files or []:
            try:
                content = await read_upload_text(upload, settings.max_file_chars)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            if content:
                uploaded_sources.append(
                    UploadedSource(filename=upload.filename or "upload.txt", content=content)
                )

        try:
            request = BlogRequest(
                topic=topic,
                tone=tone,
                audience=audience,
                word_count=word_count,
                files=uploaded_sources,
            )
            response = generate_blog(request, settings)
            response.id = save_blog(settings.database_path, request, response)
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return response.model_dump()

    return app


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "blog_generator.app:create_app",
        factory=True,
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
