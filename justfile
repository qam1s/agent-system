default:
    @just --list

run:
    uv run agent-system

dev:
    uv run uvicorn agent_system.gateway:app --reload --app-dir src

test:
    uv run pytest

lint:
    uv run ruff check .
    uv run ruff format --check .

typecheck:
    uv run ty check

check: lint typecheck test

hooks:
    uv run pre-commit install --hook-type pre-commit --hook-type pre-push
