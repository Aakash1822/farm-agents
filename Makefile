.PHONY: install dev test build clean docker-run

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	export DEBUG=True && python -m app.main

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/
	black app/ --check

format:
	black app/
	isort app/

build:
	docker build -f deployments/docker/Dockerfile -t kisan-saarthi:latest .

docker-run:
	docker-compose -f deployments/docker/docker-compose.yml up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

init-db:
	python scripts/init_db.py

seed-db:
	python scripts/seed_data.py