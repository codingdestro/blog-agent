# FINAL YEAR PROJECT REPORT

**Project Title:** Multi-Agent AI Content Engine: An Orchestrated Pipeline for Autonomous Research, Generation, and SEO Optimization.
**Academic Year:** 2025-2026
**Technology Stack:** Python (FastAPI), LangGraph, LangChain, Groq (Llama 3.3), Tavily, SQLite, Vanilla JavaScript.

---

## 1. ABSTRACT
The "Multi-Agent AI Content Engine" is an autonomous system designed to solve the challenges of modern digital content creation: time-consuming research and the need for SEO optimization. Unlike traditional "one-shot" AI tools, this project implements a **Stateful Multi-Agent Architecture** using **LangGraph**. It coordinates specialized agents to perform real-time web research, synthesize local knowledge from uploaded files, draft structured articles, and perform an analytical SEO audit. The result is a production-ready blog post that is factually grounded and optimized for search engines.

---

## 2. INTRODUCTION
### 2.1 Problem Statement
Content creators often struggle with "AI hallucinations" (fake facts) and the tedious process of optimizing drafts for search engines (SEO). Standard LLM interfaces lack the ability to browse the live web or follow a multi-step "review and refine" process.

### 2.2 Objectives
*   To implement a multi-agent system where different "experts" handle research, writing, and SEO.
*   To utilize **Retrieval-Augmented Generation (RAG)** by allowing users to upload source files.
*   To integrate real-time web search capabilities for factual grounding.
*   To provide a one-click publishing solution to professional platforms (Dev.to).

---

## 3. SYSTEM ARCHITECTURE
### 3.1 Agentic Workflow (The StateGraph)
The heart of the project is a directed acyclic graph (DAG) implemented via **LangGraph**. The state of the blog is passed through various nodes:

1.  **Search Agent (Research):** Queries the Tavily API for the latest trends and data points related to the topic.
2.  **Source Agent (Context):** Processes user-uploaded documents (TXT, PDF) and extracts relevant excerpts.
3.  **Writer Agent (Synthesis):** Takes the research data and context to draft a structured JSON-based blog post.
4.  **SEO Specialist Agent (Optimization):** Analyzes the draft to extract keywords, generate meta-descriptions, and provide structural suggestions.

### 3.2 Component Diagram
```text
[ Frontend (Vanilla JS) ] <--> [ FastAPI Backend ]
                                     |
                ---------------------------------------------
                |           LangGraph Orchestrator          |
                | (Search -> Sources -> Write -> SEO)       |
                ---------------------------------------------
                                     |
          -------------------------------------------------------
          |            |             |              |           |
       [Groq]      [Tavily]      [SQLite]      [Files]    [Dev.to]
      (Llama 3)    (Search)      (Storage)     (RAG)       (API)
```

---

## 4. TECHNICAL IMPLEMENTATION
### 4.1 Backend Engine
*   **FastAPI:** Provides a high-performance asynchronous API layer.
*   **LangGraph:** Manages the "Stateful" nature of the agents. It ensures that if the SEO agent finds an issue, the system can (in future versions) loop back to the writer.
*   **Pydantic:** Ensures strict data validation across the pipeline.

### 4.2 The SEO Specialist Logic
The SEO agent is implemented as a dedicated node that receives the "Writer's" output. It uses a lower "Temperature" setting (0.1) on the LLM to ensure analytical accuracy rather than creativity.
```python
# SEO Node Logic Snippet
def _seo_node(state: BlogState, settings: Settings) -> BlogState:
    prompt = "Analyze this blog for keywords, meta-description, and SEO suggestions..."
    response = llm.invoke(prompt)
    return {**state, "seo_data": response}
```

### 4.3 Database Schema
A normalized SQLite schema stores not just the text, but the entire metadata of the generation process, including:
*   `search_results_json`: Tracking the sources used.
*   `keywords_json`: The SEO-extracted tags.
*   `source_notes_json`: Excerpts from user files.

---

## 5. FEATURES & FUNCTIONALITIES
*   **Dynamic Research:** Fetches the most recent data (e.g., "Latest Python 3.14 features").
*   **Local RAG:** Grounds the AI in your own data by uploading research papers or notes.
*   **SEO Scorecard:** Provides a dedicated UI component showing the blog's health and discoverability.
*   **Markdown Persistence:** Stores content in professional markdown format, ready for any CMS.
*   **History Management:** A dashboard to view, re-read, or publish previously generated content.

---

## 6. RESULTS & ANALYSIS
The project successfully demonstrates that **Multi-Agent Systems (MAS)** produce higher quality output than single-prompt AI. By separating the "Writing" phase from the "Optimization" phase, the system avoids cognitive overload for the LLM, leading to:
1.  **Higher Factual Accuracy:** Due to the explicit Research step.
2.  **Better Structure:** Due to the forced JSON schema and outline nodes.
3.  **Ready-to-Publish Quality:** Due to the final SEO specialist audit.

---

## 7. CONCLUSION & FUTURE SCOPE
### 7.1 Conclusion
The AI-Agent Blog Generator fulfills all requirements of a modern AI application. It demonstrates proficiency in API integration, state management, and full-stack development.

### 7.2 Future Scope
*   **Multi-Platform Publishing:** Support for Medium, Hashnode, and WordPress.
*   **Image Generation Agent:** Integrating DALL-E or Stable Diffusion to create featured images automatically.
*   **Human-in-the-loop:** Allowing users to approve the outline before the full blog is written.

---
**Prepared By:** [Your Name]
**Project Supervisor:** [Supervisor Name]
**Date:** April 29, 2026
