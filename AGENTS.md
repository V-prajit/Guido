# Repository Guidelines

## Project Structure & Module Organization
Simulation logic lives in `sim/` (agents, physics, race loop), API surfaces in `api/`, and reusable automation in `scripts/`. The Next.js dashboard resides in `web/`, with prompts, datasets, and cached runs in `prompts/`, `data/`, `runs/`, and `cache/`. Top-level guides (`README.md`, `QUICK_START.md`, `SYSTEM_FLOW.txt`) map the flow; sample entry points (`example_integration.py`, `show_agent_profiles.py`) demonstrate agent wiring without modifying internals.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` — install Python dependencies.
- `python scripts/validate_2024.py` — verify physics parity before tuning models.
- `python scripts/comprehensive_benchmark.py` — exercise the multi-agent regression suite.
- `pytest -q` — run unit and scenario tests; add `-k pattern` for focused checks.
- `cd web && npm install` — set up the UI, then `npm run dev` for preview and `npm run lint` before commits.

## Coding Style & Naming Conventions
Target Python 3.11 + PEP 8: 4 spaces, `snake_case` variables, `PascalCase` agent classes, and type hints on public APIs. Centralize configuration near the file top and lean on `sim.agents` factories instead of bespoke constructors. Frontend code stays in TypeScript React components (`PascalCase.tsx`) with shared hooks under `web/hooks/` and lowercase Tailwind utility strings to remain consistent.

## Testing Guidelines
Each behavioral change should arrive with a `tests/test_*.py` companion using pytest assertions; echo scenario intent in the test name (`test_energy_saver_regression`). Many legacy tests print telemetry, so pair them with assertions to keep CI meaningful. Reserve heavy suites such as `tests/test_real_sim_speed.py` for pre-merge sign-off when performance-sensitive files change. Store deterministic fixtures under `tests/mock_data/` when new race inputs are needed.

## Commit & Pull Request Guidelines
Commits in this repository are short, imperative lines (e.g., “tighten adaptive harvest”), so mirror that style and keep unrelated edits separate. Mention related issues in the body and note benchmark or pytest outcomes for simulation changes. Pull requests should call out the motivation, validation steps, and any scripts teammates must rerun; include screenshots or clips for `web/` updates. Leave `.env` content and raw telemetry out of version control.

## Configuration Hygiene
Copy `.env.example` to `.env` for local runs only and avoid committing credentials. Clean transient artifacts in `cache/` and `runs/` before opening a PR so reviewers see real code changes. When adding agents or toggles, append a short note to `SYSTEM_FLOW.txt` or `CLAUDE.md` so downstream automation remains in sync.
