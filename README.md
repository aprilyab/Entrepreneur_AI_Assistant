# Entrepreneur_AI_Assistant


LLM-driven LangGraph-style assistant that helps founders and aspiring entrepreneurs across many startup directions: idea refinement, market research, funding, product planning, marketing, validation, risk analysis, and growth.


## Quick start
1. Copy `.env.example` to `.env` and add your GROQ_API_KEY and model.
2. Create virtual env: `python -m venv .venv && source .venv/bin/activate`.
3. Install requirements: `pip install -r requirements.txt` (or use poetry).
4. Run: `python -m src.main`.


## Structure
See `src/` for nodes, `src/llm` for the LLM wrapper, and `src/memory` for session memory.


**Disclaimer:** This tool is an assistant for planning startup work — not a substitute for legal, financial, or medical advice.