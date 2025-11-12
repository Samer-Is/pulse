.PHONY: help install dev build test lint clean docker-up docker-down

help:
	@echo "Pulse AI Studio - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev          Start development servers"
	@echo "  make build        Build all applications"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    Start Docker development environment"
	@echo "  make docker-down  Stop Docker environment"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove build artifacts and dependencies"

install:
	@echo "Installing dependencies..."
	pnpm install --frozen-lockfile
	cd apps/api && python -m venv .venv && .venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed"

dev:
	pnpm dev

build:
	pnpm build

test:
	pnpm test

lint:
	pnpm lint

lint-fix:
	pnpm lint:fix

format:
	pnpm format

docker-up:
	docker compose -f docker-compose.dev.yml up --build

docker-down:
	docker compose -f docker-compose.dev.yml down

docker-logs:
	docker compose -f docker-compose.dev.yml logs -f

clean:
	pnpm clean
	rm -rf apps/api/.venv
	@echo "✅ Cleaned"

