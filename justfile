default:
    @just --list

run:
    uv run uvicorn back.main:app --host 0.0.0.0 --port 8000

dev:
    uv run uvicorn back.main:app --reload

test:
    uv run pytest

front:
    uv run python -m front.main

lint:
    uv run ruff check .
    uv run ruff format --check .

typecheck:
    uv run ty check

check: lint typecheck test

hooks:
    uv run pre-commit install --hook-type pre-commit --hook-type pre-push
