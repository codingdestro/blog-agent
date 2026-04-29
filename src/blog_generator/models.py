from pydantic import BaseModel, Field


class UploadedSource(BaseModel):
    filename: str
    content: str


class BlogRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=300)
    tone: str = Field(default="clear, useful, and professional", max_length=120)
    audience: str = Field(default="general readers", max_length=120)
    word_count: int = Field(default=900, ge=300, le=3000)
    files: list[UploadedSource] = Field(default_factory=list)


class SearchResult(BaseModel):
    title: str
    url: str
    content: str = ""


class BlogSection(BaseModel):
    heading: str
    body: str


class BlogResponse(BaseModel):
    id: int | None = None
    title: str
    outline: list[str]
    summary: str = ""
    sections: list[BlogSection]
    conclusion: str = ""
    article: str
    source_notes: list[str]
    search_results: list[SearchResult]
    keywords: list[str] = Field(default_factory=list)
    meta_description: str = ""
    seo_suggestions: list[str] = Field(default_factory=list)
