# Copilot / AI agent instructions for NeuroNote

Short goal
- Help developers build, test and extend NeuroNote: an AI-enhanced EHR summarization tool.

Repository snapshot
- Root contains: `README.md` (brief project description). No other source files or config detected in workspace snapshot.

What to focus on
- This repository currently contains only documentation (`README.md`). If adding code, follow these implicit expectations:
  - Keep NLP/model code separated from web/API code (e.g., `src/model/` vs `src/api/`).
  - Keep dataset and preprocessing logic under `data/` or `src/data/` and do not commit PHI (patient data).

Critical workflows (add when present)
- Build: prefer language-native build (e.g., `npm install && npm run build` for JS/TS, `pip install -r requirements.txt` for Python). Document exact commands in `README.md` when you add them.
- Tests: add a `tests/` directory and run with the common runner for the language (e.g., `pytest` or `npm test`).
- Local model debugging: use small synthetic EHR examples in `tests/fixtures/` and mock external model calls.

Project conventions and patterns
- No project-specific files detected; use common, explicit layouts:
  - `src/` for implementation
  - `tests/` for unit/integration tests
  - `data/` for non-sensitive sample inputs
  - `notebooks/` for exploratory analysis
- Always include a short example input and expected output for summarization functions (use fixtures in `tests/fixtures/`).

Security & compliance notes
- This project is about EHRs. Never store or commit real PHI. Prefer synthetic or redacted examples in the repo.
- When adding integrations to cloud model APIs, use environment variables (e.g., `OPENAI_API_KEY`) and document them in `.env.example`.

Examples from this repo
- `README.md` explains the high-level goal: "AI Enhanced Electronic Health Record Summarization." Use that as the mission for code changes.

If you change or add files
- Update `README.md` with setup and run instructions.
- Add `LICENSE` and a `CODE_OF_CONDUCT.md` if open-source sharing is intended.

When unsure
- Ask the human maintainer for missing context: desired runtime (Python/Node), model choices, and data availability.

Please review and flag missing runtime details so I can refine these instructions.
