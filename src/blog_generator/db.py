from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .models import BlogRequest, BlogResponse


def init_db(database_path: str) -> None:
    _ensure_parent_dir(database_path)
    with _connect(database_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                outline_json TEXT NOT NULL,
                sections_json TEXT NOT NULL,
                conclusion TEXT NOT NULL DEFAULT '',
                article TEXT NOT NULL,
                source_notes_json TEXT NOT NULL,
                search_results_json TEXT NOT NULL,
                tone TEXT NOT NULL DEFAULT '',
                audience TEXT NOT NULL DEFAULT '',
                word_count INTEGER NOT NULL DEFAULT 0,
                keywords_json TEXT NOT NULL DEFAULT '[]',
                meta_description TEXT NOT NULL DEFAULT '',
                seo_suggestions_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conn.commit()


def save_blog(database_path: str, request: BlogRequest, response: BlogResponse) -> int:
    init_db(database_path)
    with closing(_connect(database_path)) as conn:
        cursor = conn.execute(
            """
            INSERT INTO blogs (
                topic,
                title,
                summary,
                outline_json,
                sections_json,
                conclusion,
                article,
                source_notes_json,
                search_results_json,
                tone,
                audience,
                word_count,
                keywords_json,
                meta_description,
                seo_suggestions_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.topic,
                response.title,
                response.summary,
                _dump_json(response.outline),
                _dump_json([section.model_dump() for section in response.sections]),
                response.conclusion,
                response.article,
                _dump_json(response.source_notes),
                _dump_json([result.model_dump() for result in response.search_results]),
                request.tone,
                request.audience,
                request.word_count,
                _dump_json(response.keywords),
                response.meta_description,
                _dump_json(response.seo_suggestions),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_blogs(database_path: str) -> list[dict]:
    init_db(database_path)
    with closing(_connect(database_path)) as conn:
        rows = conn.execute("""
            SELECT id, topic, title, summary, created_at
            FROM blogs
            ORDER BY id DESC
            """).fetchall()
    return [dict(row) for row in rows]


def list_all_blogs(database_path: str) -> list[dict]:
    init_db(database_path)
    with closing(_connect(database_path)) as conn:
        rows = conn.execute("""
            SELECT *
            FROM blogs
            ORDER BY id DESC
            """).fetchall()
    return [_decode_blog_row(row) for row in rows]


def get_blog(database_path: str, blog_id: int) -> dict | None:
    init_db(database_path)
    with closing(_connect(database_path)) as conn:
        row = conn.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,)).fetchone()
    if row is None:
        return None
    return _decode_blog_row(row)


def _decode_blog_row(row: sqlite3.Row) -> dict:
    blog = dict(row)
    blog["outline"] = _load_json(str(blog.pop("outline_json")), default=[])
    blog["sections"] = _load_json(str(blog.pop("sections_json")), default=[])
    blog["source_notes"] = _load_json(str(blog.pop("source_notes_json")), default=[])
    blog["search_results"] = _load_json(
        str(blog.pop("search_results_json")), default=[]
    )
    blog["keywords"] = _load_json(str(blog.pop("keywords_json")), default=[])
    blog["seo_suggestions"] = _load_json(
        str(blog.pop("seo_suggestions_json")), default=[]
    )
    return blog


def _connect(database_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_parent_dir(database_path: str) -> None:
    parent = Path(database_path).expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


def _dump_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True)


def _load_json(value: str, default: object) -> object:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
