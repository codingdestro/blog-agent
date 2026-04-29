# AI-Agent Blog Generator: Multi-Agent Orchestration

A sophisticated, production-ready AI content engine that automates the research, drafting, and optimization of blog posts. This project utilizes a **Multi-Agent Architecture** powered by **LangGraph** to deliver high-quality, SEO-optimized content grounded in real-time data.

## 🚀 Key Features

- **Multi-Agent Workflow:** Orchestrates specialized agents (Research, Writer, SEO Specialist) for superior content quality.
- **Real-Time Research:** Integrates **Tavily Search API** to ground articles in the latest facts and data.
- **Context-Aware Generation:** Supports file uploads (TXT, PDF, etc.) to integrate local knowledge into the AI's writing.
- **SEO Specialist Agent:** Automated analysis of every post, including keyword extraction, meta-description generation, and structural suggestions.
- **One-Click Publishing:** Direct integration with the **Dev.to API** to publish drafts instantly.
- **Stateful Persistence:** All generated content and analysis are stored in a local SQLite database.
- **Modern Responsive UI:** A clean SPA built with Vanilla JS and CSS for a fast, interactive experience.

## 🏗 Architecture Overview

The system follows an agentic pipeline managed by **LangGraph**:

1.  **Search Node:** Conducts web research based on the topic.
2.  **Source Node:** Extracts context from user-provided files.
3.  **Write Node:** Synthesizes research and context into a structured blog post using **Llama 3.3 (Groq)**.
4.  **SEO Node:** Performs an analytical audit of the draft to provide optimization data.
5.  **Publishing:** (Optional) Converts and uploads the final draft to Dev.to.

## 🛠 Setup & Installation

### Prerequisites
- Python 3.11+
- API Keys for: [Groq](https://console.groq.com/), [Tavily](https://tavily.com/), and [Dev.to](https://dev.to/settings/extensions) (Optional).

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Configuration
Edit `.env` and provide your keys:
```env
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DEVTO_API_KEY=your_key_here  # For one-click publishing
```

## ⚡ Execution

Run the application using the provided script:
```bash
./run.sh
```
The application will be available at `http://127.0.0.1:8000`.

### UI Endpoints:
- `/index.html`: Project dashboard and history.
- `/generator.html`: The main AI workspace for content generation.
- `/blog.html?id={id}`: Dedicated reader view with SEO analysis scorecard.

## 🐳 Docker Deployment

Build and run in an isolated environment:
```bash
docker build -t blog-generator .
docker run --rm -p 8000:8000 --env-file .env blog-generator
```

## 🧪 Development & Validation

- **Testing:** `pytest`
- **Linting:** `ruff check .`
- **Type Checking:** `mypy src/`

---
*Developed as a Final Year Project demonstrating Advanced AI Orchestration and Multi-Agent Systems.*
