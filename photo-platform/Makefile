.PHONY: help up down logs build test lint clean test-auth test-app test-admin

SHELL := /bin/bash

help:
	@echo "Available commands:"
	@echo "  up         - Start all services with Docker Compose"
	@echo "  down       - Stop all services with Docker Compose"
	@echo "  logs       - View logs for all services"
	@echo "  build      - Build Docker images for all services"
	@echo "  test       - Run tests for all services"
	@echo "  test-auth  - Run tests for auth service"
	@echo "  test-app   - Run tests for application service"
	@echo "  test-admin - Run tests for admin service"
	@echo "  lint       - Run linters for all services"
	@echo "  clean      - Remove Docker volumes and images"

up:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

down:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml down

logs:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f

build:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml build

test: test-auth test-app test-admin

test-auth:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm auth-service pytest

test-app:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm application-service pytest

test-admin:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm admin-service pytest

lint:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm auth-service ruff check .
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm application-service ruff check .
	docker-compose -f infrastructure/docker/docker-compose.dev.yml run --rm admin-service ruff check .

clean:
	docker-compose -f infrastructure/docker/docker-compose.dev.yml down -v --rmi all
