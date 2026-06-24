.PHONY: help install dev install-dev test lint format clean run docker-build docker-up docker-down deploy

help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean temporary files"
	@echo "  run          - Run Streamlit app"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up    - Start Docker containers"
	@echo "  docker-down  - Stop Docker containers"
	@echo "  deploy       - Deploy to production"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

install-dev:
	pip install -r requirements-dev.txt
	python -m spacy download en_core_web_sm

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/
	pylint src/ tests/
	mypy src/ tests/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

run:
	streamlit run src/main.py

docker-build:
	docker build -t ai-resume-parser .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

deploy:
	./scripts/deploy.sh