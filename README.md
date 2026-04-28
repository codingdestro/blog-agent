# Blog Generator

Python project for generating blog drafts with AI agents. It uses LangGraph for the workflow, LangChain integrations for Groq and Tavily, Groq-hosted Llama models for writing, and a static frontend served by FastAPI.

## Features

- Generate a blog from a topic.
- Upload text-like files for source context.
- Search current information automatically with Tavily.
- Draft structured blog content with a Groq Llama model.
- Use a static browser UI or call the HTTP API directly.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and add `GROQ_API_KEY` and `TAVILY_API_KEY`.
Set `DATABASE_PATH` if you want SQLite data stored somewhere other than `app.db`.

## Run

Single command:

```bash
./run.sh
```

Or manually:

```bash
uvicorn blog_generator.app:create_app --factory --reload
```

Open `http://127.0.0.1:8000`.

Frontend pages:

- `/index.html`: project landing page.
- `/generator.html`: blog generation page.
- `/blog.html?id={blog_id}`: saved blog detail page.

## Docker

Build the image:

```bash
docker build -t blog-generator .
```

Run the container:

```bash
docker run --rm -p 8000:8000 \
  -e GROQ_API_KEY=your_groq_api_key \
  -e TAVILY_API_KEY=your_tavily_api_key \
  -e GROQ_MODEL=llama-3.3-70b-versatile \
  blog-generator
```

Open `http://127.0.0.1:8000`.

## API

`POST /api/generate`

Multipart form fields:

- `topic`: required blog topic.
- `tone`: optional writing tone.
- `audience`: optional target audience.
- `word_count`: optional approximate target length.
- `files`: optional uploaded source files.

The response contains the generated title, outline, article, source notes, and search results.
Generated blogs are saved to SQLite after successful generation.

Saved blog endpoints:

- `GET /api/blogs`: list all saved blogs with full structured content.
- `GET /api/blogs/summaries`: list saved blog summaries.
- `GET /api/blogs/{blog_id}`: fetch one saved blog with structured fields.

## Validate

```bash
pytest
ruff check .
```
