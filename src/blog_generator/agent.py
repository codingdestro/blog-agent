from __future__ import annotations

import json
from typing import Any, TypedDict

from .config import Settings
from .db import get_blog
from .models import BlogRequest, BlogResponse, BlogSection, SearchResult


class BlogState(TypedDict, total=False):
    request: BlogRequest
    search_results: list[SearchResult]
    source_notes: list[str]
    title: str
    outline: list[str]
    summary: str
    sections: list[BlogSection]
    conclusion: str
    article: str
    keywords: list[str]
    meta_description: str
    seo_suggestions: list[str]


def generate_blog(request: BlogRequest, settings: Settings) -> BlogResponse:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is required to generate a blog")

    graph = _build_graph(settings)
    state = graph.invoke({"request": request})

    return BlogResponse(
        title=state["title"],
        outline=state["outline"],
        summary=state["summary"],
        sections=state["sections"],
        conclusion=state["conclusion"],
        article=state["article"],
        source_notes=state["source_notes"],
        search_results=state["search_results"],
        keywords=state.get("keywords", []),
        meta_description=state.get("meta_description", ""),
        seo_suggestions=state.get("seo_suggestions", []),
    )


def upload_blog(blog_id: int, settings: Settings) -> dict[str, Any]:
    if not settings.devto_api_key:
        raise RuntimeError("DEVTO_API_KEY is required to upload a blog")
    blog = _fetch_blog_from_db(settings.database_path, blog_id)
    return _build_publish_blog(blog, settings)


def _fetch_blog_from_db(database_path: str, blog_id: int):
    blog = get_blog(database_path, blog_id)
    if not blog:
        raise RuntimeError(f"Blog with id {blog_id} not found")
    return blog


def _build_publish_blog(blog: dict, settings: Settings):
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError(
            "langchain-groq and langchain-core are required for generation"
        ) from exc

    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.45,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    payload = blog

    messages = [
        SystemMessage(
            content=(
                "You are a careful json to blog schema converter. Use the supplied json blog and "
                "convert it to a valid blog post schema. The input JSON may contain the following fields: "
                "title, content, tags, description. "
                "conent must a proper mardown format with heading list etc."
                "Do not wrap the JSON in markdown. The JSON object must match this schema: "
                "{'title':'string','content':'string','tags':'string','description':'string'}. "
            )
        ),
        HumanMessage(content=json.dumps(payload, ensure_ascii=True)),
    ]
    response = llm.invoke(messages)
    parsed = _parse_llm_json(str(response.content))
    # print(parsed.get("content"))
    try:
        _publish_to_devto(
            title=parsed.get("title", "Untitled Blog"),
            content=parsed.get("content", ""),
            tags=parsed.get("tags", ""),
            description=parsed.get("description", ""),
            api_key=settings.devto_api_key,
        )
        return {"status": "published"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _publish_to_devto(title, content, tags, description, api_key):
    print("Publishing to Dev.to with title:", title)
    import requests

    url = "https://dev.to/api/articles"

    headers = {"api-key": api_key, "Content-Type": "application/json"}

    data = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": content,
            "tags": tags,
            "description": description,
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def _build_graph(settings: Settings) -> Any:
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "langgraph is not installed. Run `pip install -e .`."
        ) from exc

    graph = StateGraph(BlogState)
    graph.add_node("search", lambda state: _search_node(state, settings))
    graph.add_node("sources", _source_node)
    graph.add_node("write", lambda state: _write_node(state, settings))
    graph.add_node("seo", lambda state: _seo_node(state, settings))

    graph.set_entry_point("search")
    graph.add_edge("search", "sources")
    graph.add_edge("sources", "write")
    graph.add_edge("write", "seo")
    graph.add_edge("seo", END)
    return graph.compile()


def _search_node(state: BlogState, settings: Settings) -> BlogState:
    request = state.get("request")
    results: list[SearchResult] = []

    if settings.tavily_api_key:
        try:
            from langchain_community.tools.tavily_search import \
                TavilySearchResults
        except ImportError as exc:
            raise RuntimeError(
                "langchain-community is required for Tavily search"
            ) from exc

        tool = TavilySearchResults(
            max_results=settings.max_search_results,
            tavily_api_key=settings.tavily_api_key,
        )
        raw_results = tool.invoke(
            {"query": f"{request.topic} latest facts data examples"}
        )
        results = [_normalize_search_result(item) for item in raw_results]

    return {**state, "search_results": results}


def _source_node(state: BlogState) -> BlogState:
    request = state.get("request")
    notes = []

    for source in request.files:
        excerpt = source.content.replace("\n", " ").strip()[:280]
        if excerpt:
            notes.append(f"{source.filename}: {excerpt}")

    return {**state, "source_notes": notes}


def _write_node(state: BlogState, settings: Settings) -> BlogState:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError(
            "langchain-groq and langchain-core are required for generation"
        ) from exc

    request = state.get("request")
    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.45,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    payload = {
        "topic": request.topic,
        "tone": request.tone,
        "audience": request.audience,
        "target_word_count": request.word_count,
        "source_notes": state.get("source_notes", []),
        "search_results": [
            result.model_dump() for result in state.get("search_results", [])
        ],
    }

    messages = [
        SystemMessage(
            content=(
                "You are a careful blog-writing agent. Use the supplied file context and "
                "search results when available. Do not invent citations. Return only valid JSON. "
                "Do not wrap the JSON in markdown. The JSON object must match this schema: "
                '{"title":"string","summary":"string","outline":["string"],'
                '"sections":[{"heading":"string","body":"string"}],'
                '"conclusion":"string"}. Make sections substantial and ordered.'
            )
        ),
        HumanMessage(content=json.dumps(payload, ensure_ascii=True)),
    ]
    response = llm.invoke(messages)
    parsed = _parse_llm_json(str(response.content))
    sections = _coerce_sections(parsed.get("sections"))
    article = _compose_article(
        summary=str(parsed.get("summary") or "").strip(),
        sections=sections,
        conclusion=str(parsed.get("conclusion") or "").strip(),
        fallback=str(parsed.get("article") or "").strip(),
    )

    return {
        **state,
        "title": str(parsed.get("title") or request.topic).strip(),
        "outline": _coerce_outline(parsed.get("outline")),
        "summary": str(parsed.get("summary") or "").strip(),
        "sections": sections,
        "conclusion": str(parsed.get("conclusion") or "").strip(),
        "article": article,
    }


def _seo_node(state: BlogState, settings: Settings) -> BlogState:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError(
            "langchain-groq and langchain-core are required for analysis"
        ) from exc

    article = state.get("article", "")
    title = state.get("title", "")

    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.1,  # Lower temperature for analytical task
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    prompt = (
        "You are an SEO Specialist agent. Analyze the following blog post and title. "
        "Extract key keywords, generate a compelling meta description (max 160 chars), "
        "and provide 3-5 actionable SEO suggestions (e.g., 'Add a call to action', 'Use more descriptive subheadings'). "
        "Return the results in the following JSON format: "
        '{"keywords": ["word1", "word2"], "meta_description": "string", "suggestions": ["suggestion1", "suggestion2"]}. '
        "Do not wrap the JSON in markdown.\n\n"
        f"Title: {title}\n"
        f"Content: {article[:4000]}"  # Limit content to stay within context limits if blog is very long
    )

    messages = [
        SystemMessage(content="You are a professional SEO analyzer."),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    parsed = _parse_llm_json(str(response.content))

    return {
        **state,
        "keywords": parsed.get("keywords", []),
        "meta_description": parsed.get("meta_description", ""),
        "seo_suggestions": parsed.get("suggestions", []),
    }


def _normalize_search_result(item: Any) -> SearchResult:
    if isinstance(item, SearchResult):
        return item
    if not isinstance(item, dict):
        return SearchResult(title="Search result", url="", content=str(item))

    return SearchResult(
        title=str(item.get("title") or item.get("url") or "Search result"),
        url=str(item.get("url") or ""),
        content=str(item.get("content") or item.get("snippet") or ""),
    )


def _parse_llm_json(content: str) -> dict[str, Any]:
    cleaned = _extract_json_object(content)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("The model returned invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("The model returned JSON, but not an object")
    return parsed


def _extract_json_object(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    start = cleaned.find("{")
    if start == -1:
        return cleaned

    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(cleaned[start:], start=start):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return cleaned[start : index + 1]

    return cleaned[start:]


def _coerce_outline(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [line.strip("- ").strip() for line in value.splitlines() if line.strip()]
    return []


def _coerce_sections(value: Any) -> list[BlogSection]:
    if not isinstance(value, list):
        return []

    sections: list[BlogSection] = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, dict):
            heading = str(
                item.get("heading") or item.get("title") or f"Section {index}"
            ).strip()
            body = str(item.get("body") or item.get("content") or "").strip()
        else:
            heading = f"Section {index}"
            body = str(item).strip()

        if body:
            sections.append(BlogSection(heading=heading, body=body))

    return sections


def _compose_article(
    summary: str,
    sections: list[BlogSection],
    conclusion: str,
    fallback: str,
) -> str:
    parts = []
    if summary:
        parts.append(summary)
    parts.extend(f"{section.heading}\n{section.body}" for section in sections)
    if conclusion:
        parts.append(f"Conclusion\n{conclusion}")
    return "\n\n".join(parts).strip() or fallback
