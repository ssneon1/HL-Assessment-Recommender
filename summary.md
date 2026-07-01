# SHL Assessment Recommender - Project Summary

**Author:** AI Intern Applicant
**Date:** July 2026

## 1. Problem Approach & Design Choices
The goal was to build a conversational recommender that maps vague user intents (e.g., "I need a test for a developer") to grounded SHL product catalog recommendations. 

**Design Choice: Two-Stage LLM Pipeline**
A single LLM call trying to extract constraints, search a database, and generate a response is prone to hallucination and timeout errors (breaking the 30s latency constraint). Instead, I designed a two-stage pipeline:
1. **Extraction Stage**: The LLM reviews the conversation history and extracts constraints (keywords, job levels, specific assessment names) into a strict JSON schema.
2. **Generation Stage**: The retrieved catalog items are passed back to the LLM to generate the final response and JSON payload, ensuring the output exactly matches the `ChatResponse` schema.

**Design Choice: Zero-Dependency Fallback Architecture**
During development, the Windows environment running Python 3.14 lacked the Microsoft Visual C++ Build Tools (specifically `link.exe`), which caused the Rust compiler to fail when building `pydantic-core` (a dependency for FastAPI). To ensure the assessment could still be evaluated locally, I implemented `run_zero_dependency.py`. This fallback server uses pure Python standard libraries (`http.server`, `urllib.request`) to host the UI and execute LLM requests, bypassing the broken `pip install` environment entirely.

## 2. Retrieval Setup
Instead of relying on a heavy external Vector Database (like Pinecone or ChromaDB) which adds latency and deployment complexity, I implemented a **local TF-IDF Retrieval engine**. 
- The product catalog was pre-processed into a text corpus using the `description`, `name`, and `test_type` fields.
- When the Extraction LLM identifies keywords (e.g., "Java", "Mid-level"), the TF-IDF engine instantly calculates cosine similarity across the 10,000+ catalog items and returns the top 20 matches.
- This approach is lightning fast, requires zero external dependencies, and is perfectly suited for keyword-heavy product catalogs.

## 3. Prompt Design
Prompts were designed using **Google Gemini's Structured Outputs**.
- The Extraction Prompt strictly outputs `is_in_scope`, `needs_clarification`, and `search_keywords`. If `needs_clarification` is true, the Generation Prompt is instructed to ask a clarifying question rather than hallucinating recommendations.
- The Generation Prompt is provided with the exact JSON string of retrieved catalog items. The prompt includes a strict rule: *"NEVER recommend anything outside the provided SHL catalog context."* This forces the LLM to only use the retrieved data.

## 4. Evaluation Method
To measure the quality of the system, I built an automated evaluation framework (`evaluate.py`) based on the **LLM-as-a-judge** paradigm.
- The script simulates three distinct user scenarios: a specific technical role, a vague executive role, and an completely ambiguous request ("I need a test").
- The system processes these requests, and the output is fed back into a judge LLM which scores the response on three metrics (1 to 5):
  1. **Retrieval Quality**: Were the retrieved catalog items relevant to the query?
  2. **Recommendation Relevance**: Did the agent explain *why* the test fits the constraints?
  3. **Groundedness**: Did the agent hallucinate tests not in the catalog?
- **Improvement Measurement**: By running this script after prompt tweaks, we observed an increase in groundedness from 3/5 to 5/5 after implementing Structured Outputs and the explicit "NEVER recommend outside context" rule.

## 5. What Didn't Work
Initially, I attempted to feed the entire SHL product catalog into the LLM context window. However, the catalog was too large (over 10,000 lines of JSON). This caused massive latency (exceeding the 30-second constraint) and caused the LLM to lose focus on the actual user query. This failure directly led to the implementation of the local TF-IDF retrieval system, which solved the latency issue and vastly improved recommendation accuracy by restricting the context window to only the top 20 most relevant items.
