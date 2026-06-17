.PHONY: help setup build up down restart logs shell db-migrate db-upgrade db-downgrade test clean format lint

SHELL := /bin/bash

help:
	@echo "Доступные команды:"
	@echo "  make setup        - Полная установка и запуск проекта с нуля"
	@echo "  make build        - Собрать Docker образы"
	@echo "  make up           - Запустить все сервисы"
	@echo "  make down         - Остановить все сервисы"
	@echo "  make restart      - Перезапустить все сервисы"
	@echo "  make logs         - Показать логи всех сервисов"
	@echo "  make shell        - Войти в контейнер приложения"
	@echo "  make db-migrate   - Создать новую миграцию БД"
	@echo "  make db-upgrade   - Применить миграции БД"
	@echo "  make db-downgrade - Откатить последнюю миграцию"
	@echo "  make test         - Запустить тесты"
	@echo "  make clean        - Очистить кеш и временные файлы"
	@echo "  make format       - Форматировать код"
	@echo "  make lint         - Проверить код линтерами"

setup:
	@echo "==> TrackFit Pro: начальная настройка <=="
	@if [ -f .env ]; then \
		echo ".env уже существует"; \
	else \
		cp .env.example .env; \
		echo ".env создан из .env.example"; \
	fi
	@mkdir -p logs
	@echo "==> Сборка Docker образов <=="
	docker-compose build
	@echo "==> Запуск сервисов <=="
	docker-compose up -d
	@echo "==> Ожидание готовности сервисов <=="
	@for i in $$(seq 1 30); do \
		docker-compose exec -T api python -c "print('ready')" 2>/dev/null && break; \
		echo "Ожидание запуска... $$i/30"; \
		sleep 2; \
	done
	@echo "==> Применение миграций <=="
	docker-compose exec api alembic upgrade head
	@echo ""
	@echo "==> Готово! <=="
	@echo "API:               http://localhost:8000"
	@echo "Swagger docs:      http://localhost:8000/docs"
	@echo "ReDoc:             http://localhost:8000/redoc"
	@echo "Health:            http://localhost:8000/health"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Приложение запущено на http://localhost:8000"
	@echo "API документация доступна на http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec api bash

db-migrate:
	docker-compose exec api alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	docker-compose exec api alembic upgrade head

db-downgrade:
	docker-compose exec api alembic downgrade -1

test:
	docker-compose exec api pytest -v --cov=src --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

format:
	docker-compose exec api ruff check --fix src tests
	docker-compose exec api ruff format src tests

lint:
	docker-compose exec api ruff check src tests
	docker-compose exec api mypy src
	docker-compose exec api ruff format --check src tests
