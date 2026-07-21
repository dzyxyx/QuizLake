# QuizLake

QuizLake — веб-платформа для проведения интерактивных викторин в реальном времени.

Проект состоит из двух частей:

- **backend** — серверное REST API и WebSocket-слой для проведения live-сессий (Python/FastAPI).
- **frontend** — одностраничное веб-приложение (SPA) для ведущих и участников (Vue 3/TypeScript).

## Функциональность

- Регистрация и вход по email/паролю, JWT-аутентификация с access- и refresh-токенами.
- Создание и редактирование квизов: черновик → готов к публикации → архив (после завершённых сессий квиз архивируется, а не удаляется).
- Вопросы с вариантами ответов, ограничением по времени и баллами за правильный ответ.
- Выбор категории квиза из справочника категорий.
- Запуск live-сессии с уникальным кодом комнаты; присоединение участников по коду.
- Синхронная игра в реальном времени через WebSocket: вопросы, ответы, раскрытие правильного варианта с процентами по каждому варианту ответа.
- Защита от участия ведущего в собственной сессии как игрока.
- Раздел «Обзор» — публичные квизы и активные/запланированные сессии других ведущих.
- Профиль пользователя: статистика (проведено квизов, сыграно квизов) и история участий с переходом к результатам.

## Стек технологий

| Компонент | Технология |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) + asyncpg |
| СУБД | PostgreSQL 16 |
| Миграции БД | Alembic |
| Аутентификация | JWT (python-jose), passlib/bcrypt |
| Frontend | Vue 3 (Composition API) + TypeScript, Pinia, Vue Router, Vite |
| Тестирование | pytest / pytest-asyncio (backend), Vitest / vue-tsc (frontend) |
| Инфраструктура | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions (тесты при push/PR в `main`) |

## Структура проекта

```
QuizLake/
├── backend/                     # FastAPI-приложение
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST-эндпоинты (auth, quizzes, questions, quiz_sessions, users, categories, ws)
│   │   ├── core/                # конфиг (Settings) и security (JWT, хеширование паролей)
│   │   ├── db/
│   │   │   ├── models/          # SQLAlchemy-модели
│   │   │   └── session.py       # engine и фабрика асинхронных сессий БД
│   │   ├── schemas/             # Pydantic-схемы запросов/ответов
│   │   ├── websockets/          # менеджер WebSocket-соединений живой сессии
│   │   └── main.py              # точка входа FastAPI
│   ├── alembic/versions/        # миграции БД
│   ├── tests/                   # pytest-тесты
│   ├── docker-compose.yml       # postgres + backend + frontend
│   └── Dockerfile
├── frontend/                    # Vue 3 SPA
│   ├── src/
│   │   ├── api/                 # обёртки над REST-запросами
│   │   ├── components/          # переиспользуемые компоненты
│   │   ├── composables/         # composable-функции (WebSocket-подключение и т.д.)
│   │   ├── layouts/             # layout-обёртки страниц
│   │   ├── router/              # маршрутизация и guard-ы доступа
│   │   ├── stores/              # Pinia-хранилища (auth, quizzes, session, categories, ...)
│   │   ├── views/               # экраны приложения
│   │   └── types/               # общие TypeScript-типы
│   ├── tests/                   # Vitest-тесты
│   └── Dockerfile
└── .github/workflows/           # CI (GitHub Actions)
```

## Как запустить проект

Проект поднимается целиком через Docker Compose (Postgres + backend + frontend одной командой).

1. Перейдите в папку `backend/` — файл `docker-compose.yml` находится там:
   ```bash
   cd backend
   ```
2. Создайте `.env` на основе примера и заполните значения (пароли, `SECRET_KEY` и т.д.):
   ```bash
   cp .env.example .env
   ```
3. Поднимите все сервисы:
   ```bash
   docker compose up -d --build
   ```

После запуска:
- Frontend доступен на `http://localhost` (порт 80).
- Backend API — на `http://localhost:8000`.

При старте backend-контейнера автоматически применяются миграции (`alembic upgrade head`), включая сид дефолтных категорий — отдельно накатывать миграции вручную не нужно.

### Локальная разработка без Docker

- **Backend**: `pip install -r requirements/dev.txt`, затем `alembic upgrade head` и `uvicorn app.main:app --reload`.
- **Frontend**: `npm install`, затем `npm run dev` (см. `frontend/.env.example` для переменных `VITE_API_BASE_URL`/`VITE_WS_BASE_URL`).

## Переменные окружения

### backend/.env

| Переменная | Описание | Пример/по умолчанию |
|---|---|---|
| `PROJECT_NAME` | Название проекта (используется в заголовке API) | `QuizLake` |
| `ENVIRONMENT` | Окружение приложения | `development` |
| `DEBUG` | Режим отладки FastAPI | `True` |
| `SECRET_KEY` | Секрет для подписи JWT | сгенерировать: `openssl rand -hex 32` |
| `POSTGRES_HOST` | Хост PostgreSQL | `localhost` (в Docker — `postgres`) |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_DB` | Имя базы данных | `QuizLake_db` |
| `POSTGRES_USER` | Пользователь БД | `quizlake_user` |
| `POSTGRES_PASSWORD` | Пароль БД | — |
| `ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Срок жизни access-токена, мин | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Срок жизни refresh-токена, дней | `30` |
| `ALLOWED_ORIGINS` | Список разрешённых CORS-origin (JSON-массив) | `["http://localhost:5173","http://localhost"]` |

### frontend/.env

| Переменная | Описание | Пример/по умолчанию |
|---|---|---|
| `VITE_API_BASE_URL` | Базовый URL REST API | `http://localhost:8000/api/v1` |
| `VITE_WS_BASE_URL` | Базовый URL WebSocket | `ws://localhost:8000/api/v1` |

Оба файла собираются на этапе сборки Vite (значения «зашиваются» в бандл), поэтому при изменении `VITE_*` фронтенд нужно пересобрать.

## Тестирование

### Backend

Тесты работают поверх реальной PostgreSQL (не sqlite/мок), поэтому нужна доступная база — проще всего использовать уже поднятый через Docker Compose сервис `postgres`.

```bash
cd backend
pip install -r requirements/dev.txt

export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=quizlake_user
export POSTGRES_PASSWORD=quizlake_secret
export POSTGRES_DB=quizlake_test_db   # отдельная тестовая БД, создаётся автоматически
export PROJECT_NAME=QuizLake ENVIRONMENT=test DEBUG=True
export SECRET_KEY=test_secret ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=60 REFRESH_TOKEN_EXPIRE_DAYS=30
export ALLOWED_ORIGINS='["http://localhost:5173"]'

pytest -q
```

Схема БД создаётся и очищается автоматически фикстурами в `tests/conftest.py` — вручную накатывать миграции для тестов не требуется. Именно так тесты гоняются и в GitHub Actions (см. `.github/workflows/ci.yml`).

### Frontend

```bash
cd frontend
npm install
npx vue-tsc -b     # проверка типов
npm run test       # Vitest
```

## Документация

- **Интерактивная документация API (Swagger UI)** — `http://localhost:8000/docs`.
- **ReDoc** — `http://localhost:8000/redoc`.
- **Postman-коллекция** — `backend/QuizLake.postman_collection.json`.
