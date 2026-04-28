from blog_generator.db import get_blog, list_all_blogs, list_blogs, save_blog
from blog_generator.models import BlogRequest, BlogResponse, BlogSection, SearchResult


def test_save_and_get_blog(tmp_path) -> None:
    database_path = str(tmp_path / "blogs.db")
    request = BlogRequest(topic="AI agents", tone="clear", audience="students", word_count=500)
    response = BlogResponse(
        title="AI Agents",
        outline=["Intro", "Use cases"],
        summary="A short summary.",
        sections=[BlogSection(heading="Intro", body="Body text.")],
        conclusion="Final thought.",
        article="Full article",
        source_notes=["notes"],
        search_results=[SearchResult(title="Result", url="https://example.com", content="Snippet")],
    )

    blog_id = save_blog(database_path, request, response)

    saved = get_blog(database_path, blog_id)
    assert saved is not None
    assert saved["id"] == blog_id
    assert saved["topic"] == "AI agents"
    assert saved["outline"] == ["Intro", "Use cases"]
    assert saved["sections"][0]["heading"] == "Intro"
    assert saved["search_results"][0]["url"] == "https://example.com"

    summaries = list_blogs(database_path)
    assert summaries[0]["id"] == blog_id
    assert summaries[0]["title"] == "AI Agents"

    all_blogs = list_all_blogs(database_path)
    assert all_blogs[0]["id"] == blog_id
    assert all_blogs[0]["article"] == "Full article"
    assert all_blogs[0]["sections"][0]["body"] == "Body text."
