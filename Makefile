.PHONY: help install setup-db migrate test run-backend run-mobile clean docker-up docker-down

help:
	@echo "NIRBHAYA Development Commands"
	@echo "=============================="
	@echo "make install      - Install Python dependencies"
	@echo "make setup-db     - Set up database with PostGIS"
	@echo "make migrate      - Run database migrations"
	@echo "make test         - Run all tests"
	@echo "make test-cov     - Run tests with coverage"
	@echo "make run-backend  - Run backend API server"
	@echo "make run-mobile   - Run mobile client"
	@echo "make docker-up    - Start PostgreSQL and Redis with Docker"
	@echo "make docker-down  - Stop Docker services"
	@echo "make clean        - Clean up generated files"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

setup-db:
	python scripts/setup_db.py

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

test:
	pytest

test-cov:
	pytest --cov=backend --cov-report=html --cov-report=term

test-unit:
	pytest -m unit

test-property:
	pytest -m property

test-integration:
	pytest -m integration

run-backend:
	python backend/main.py

run-mobile:
	python mobile/main.py

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@docker-compose ps

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".hypothesis" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage

format:
	black backend/ mobile/ tests/

lint:
	flake8 backend/ mobile/ tests/

check: format lint test
