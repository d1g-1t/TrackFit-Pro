# TrackFit Pro API

Профессиональный REST API для отслеживания фитнес-активности с расширенной аналитикой тренировок, построенный на FastAPI с использованием лучших практик Python разработки.

## Основные возможности

- 🏃 **Управление тренировками**: Создание, редактирование и отслеживание различных типов тренировок (бег, ходьба, плавание, велоспорт, йога, силовые тренировки)
- 📊 **Аналитика и статистика**: Расширенная аналитика тренировок с расчетом калорий, скорости, дистанции и пульсовых зон
- 🎯 **Система целей**: Установка и отслеживание фитнес-целей с прогрессом в реальном времени
- 👤 **Управление пользователями**: Регистрация, аутентификация и профили пользователей
- ⚡ **Кэширование Redis**: Оптимизированная производительность с кэшированием часто запрашиваемых данных
- 🔒 **Безопасность**: JWT аутентификация, хэширование паролей с bcrypt
- 📝 **Логирование**: Подробное логирование на русском языке

## Технологический стек

- **FastAPI** - Современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **PostgreSQL** - Реляционная база данных
- **Redis** - Кэширование и хранилище данных в памяти
- **Alembic** - Миграции базы данных
- **Pydantic** - Валидация данных
- **UV** - Быстрый менеджер пакетов Python
- **Docker & Docker Compose** - Контейнеризация

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Make

### Запуск проекта

```bash
git clone <repository-url>
cd trackfit-pro
make setup
```

`make setup` автоматически: создаёт `.env` из `.env.example`, собирает Docker-образы, запускает все сервисы, ждёт их готовности и применяет миграции БД.

После завершения:

- API: http://localhost:8000
- Документация Swagger: http://localhost:8000/docs
- Документация ReDoc: http://localhost:8000/redoc

## Доступные команды Make

| Команда | Описание |
|---------|----------|
| `make setup` | Полная установка и запуск с нуля одной командой |
| `make build` | Собрать Docker образы |
| `make up` | Запустить все сервисы |
| `make down` | Остановить все сервисы |
| `make restart` | Перезапустить все сервисы |
| `make logs` | Показать логи всех сервисов |
| `make shell` | Войти в контейнер приложения |
| `make db-migrate` | Создать новую миграцию БД |
| `make db-upgrade` | Применить миграции БД |
| `make db-downgrade` | Откатить последнюю миграцию |
| `make test` | Запустить тесты |
| `make clean` | Очистить кеш и временные файлы |
| `make format` | Форматировать код |
| `make lint` | Проверить код линтерами |

## Структура проекта

```
trackfit-pro/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── users.py       # Endpoints пользователей
│   │   │   ├── workouts.py    # Endpoints тренировок
│   │   │   └── goals.py       # Endpoints целей
│   │   └── dependencies.py    # Зависимости FastAPI
│   ├── core/
│   │   ├── config.py          # Конфигурация приложения
│   │   ├── database.py        # Подключение к БД
│   │   ├── cache.py           # Redis кэширование
│   │   ├── security.py        # Аутентификация и безопасность
│   │   ├── logging.py         # Настройка логирования
│   │   ├── exceptions.py      # Кастомные исключения
│   │   └── middleware.py       # Промежуточное ПО
│   ├── models/
│   │   └── models.py          # SQLAlchemy модели
│   ├── schemas/
│   │   ├── user.py            # Pydantic схемы пользователей
│   │   ├── workout.py         # Pydantic схемы тренировок
│   │   └── goal.py            # Pydantic схемы целей
│   ├── services/
│   │   ├── analytics.py       # Бизнес-логика аналитики
│   │   ├── user_service.py    # Сервис пользователей
│   │   ├── workout_service.py # Сервис тренировок
│   │   └── goal_service.py    # Сервис целей
│   └── main.py                # Точка входа приложения
├── alembic/                   # Миграции БД
├── tests/                     # Тесты
├── docker-compose.yml         # Конфигурация Docker
├── Dockerfile                 # Образ приложения
├── Makefile                   # Команды управления
├── pyproject.toml             # UV зависимости
└── README.md                  # Документация

```

## API Endpoints

### Пользователи

- `POST /api/v1/users/register` - Регистрация
- `POST /api/v1/users/login` - Вход
- `GET /api/v1/users/me` - Получить текущего пользователя
- `PUT /api/v1/users/me` - Обновить профиль
- `DELETE /api/v1/users/me` - Удалить аккаунт

### Тренировки

- `POST /api/v1/workouts` - Создать тренировку
- `GET /api/v1/workouts` - Получить список тренировок
- `GET /api/v1/workouts/stats` - Получить статистику
- `GET /api/v1/workouts/{id}` - Получить тренировку
- `PUT /api/v1/workouts/{id}` - Обновить тренировку
- `DELETE /api/v1/workouts/{id}` - Удалить тренировку

### Цели

- `POST /api/v1/goals` - Создать цель
- `GET /api/v1/goals` - Получить список целей
- `GET /api/v1/goals/{id}` - Получить цель
- `GET /api/v1/goals/{id}/progress` - Получить прогресс цели
- `PUT /api/v1/goals/{id}` - Обновить цель
- `DELETE /api/v1/goals/{id}` - Удалить цель

## Типы тренировок

- `running` - Бег
- `walking` - Ходьба
- `swimming` - Плавание
- `cycling` - Велоспорт
- `strength` - Силовые тренировки
- `yoga` - Йога
- `other` - Другое

## Примеры использования

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "athlete",
    "password": "securepass123",
    "weight": 75.0,
    "height": 180.0,
    "age": 25
  }'
```

### Создание тренировки

```bash
curl -X POST "http://localhost:8000/api/v1/workouts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workout_type": "running",
    "duration_minutes": 45,
    "distance_km": 8.5,
    "average_heart_rate": 145,
    "started_at": "2025-11-12T10:00:00"
  }'
```

### Получение статистики

```bash
curl -X GET "http://localhost:8000/api/v1/workouts/stats?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Разработка

### Локальная разработка без Docker

1. **Установите UV**

```bash
pip install uv
```

2. **Установите зависимости**

```bash
uv sync --all-extras
```

3. **Настройте PostgreSQL и Redis локально**

4. **Запустите приложение**

```bash
uvicorn src.main:app --reload
```

### Создание миграции

```bash
make db-migrate msg="описание изменений"
```

### Запуск тестов

```bash
make test
```

### Форматирование кода

```bash
make format
```

## Лицензия

MIT License

## Контакты

Для вопросов и предложений создайте issue в репозитории проекта.
