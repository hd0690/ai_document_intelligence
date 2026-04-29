.PHONY: help install dev test clean run setup-check

help:
	@echo "Document Intelligence Tool - Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make setup-check  - Check system requirements"
	@echo "  make ingest       - Ingest sample documents"
	@echo "  make query        - Run sample query"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests.py -v

lint:
	ruff check .
	mypy --ignore-missing-imports .

format:
	black .
	ruff check --fix .

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

setup-check:
	python setup_check.py

example:
	python example.py

ingest:
	@echo "Creating sample document..."
	@mkdir -p data/docs
	@echo "Python is a versatile programming language. It's known for its readability and simplicity. Python supports multiple programming paradigms." > data/docs/sample.txt
	@echo "Ingesting documents..."
	docintel ingest ./data/docs

query:
	docintel ask "What is Python?" --debug

info:
	docintel info

clear:
	docintel clear-db
