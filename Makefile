MIGRATION_MESSAGE ?= auto

revision:
	docker compose run --rm alembic-revision alembic revision --autogenerate -m "$(MIGRATION_MESSAGE)"

build:
	docker compose up -d --build

up:
	docker compose up -d

down:
	docker compose down