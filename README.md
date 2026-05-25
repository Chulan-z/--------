# Агрегатор новостей из различных источников

Учебное fullstack-приложение для сбора новостей из RSS-источников, хранения их в PostgreSQL и просмотра через темный Angular-интерфейс. Backend реализован на FastAPI, доступ к данным выполнен через SQLAlchemy, миграции ведутся Alembic, авторизация построена на JWT access + refresh токенах.

## Структура проекта

```text
backend/
  alembic/versions/20260528_0001_initial_schema.py
  app/
    api/              REST-маршруты auth, news, profile, admin
    core/             конфигурация и JWT/bcrypt
    db/               SQLAlchemy engine/session/base
    models/           ORM-модели таблиц PostgreSQL
    schemas/          Pydantic-схемы валидации
    services/         RSS-агрегатор, аудит, backup, migrations, seed
  scripts/            PowerShell-скрипты pg_dump/pg_restore
  sql/schema.sql      SQL-схема БД
  tests/              pytest-тесты API, auth, RBAC, backup, security
frontend/
  src/app/pages/      лента, вход, регистрация, кабинет, админка
  src/app/services/   API/Auth-сервисы и JWT interceptor
  src/app/guards/     auth/admin guard
reports/              ежедневные отчеты по практике
scripts/              shell-скрипты backup/restore и daily commits
```

## Анализ предметной области

Новостной агрегатор нужен пользователю, чтобы читать материалы из разных источников в одной ленте без ручного обхода сайтов. Основные сущности предметной области: пользователь, роль, источник новостей, статья, категория, журнал действий, refresh-сессия и резервная копия БД. Приложение поддерживает регистрацию, авторизацию, просмотр ленты, управление профилем, администрирование источников, запуск агрегации, аудит действий и резервное копирование.

## Архитектура и стек

Выбрана трехзвенная архитектура: Angular-клиент, FastAPI REST API и PostgreSQL. Angular подходит для SPA с guard-ами и сервисами, FastAPI дает строгую Pydantic-валидацию и удобную OpenAPI-документацию, PostgreSQL надежно хранит связанные данные, JSON-права ролей, индексы и ограничения. SQLAlchemy защищает от SQL-инъекций за счет параметризованных запросов ORM, Alembic фиксирует изменения схемы.

## База данных PostgreSQL

Приоритет дня 4 выполнен в [backend/sql/schema.sql](backend/sql/schema.sql) и миграции [backend/alembic/versions/20260528_0001_initial_schema.py](backend/alembic/versions/20260528_0001_initial_schema.py).

Таблицы:

- `roles`: роли `user`, `admin`, массив прав `permissions`.
- `users`: учетные записи, `password_hash`, FK на `roles`, активность и даты.
- `news_sources`: RSS/API-источники, URL уникален, тип ограничен `rss/api`.
- `categories`: справочник категорий.
- `news_articles`: новости, FK на источник и категорию, уникальный URL.
- `logs`: аудит входов, ошибок, действий пользователей и администраторов.
- `refresh_tokens`: refresh-сессии с истечением и отзывом.
- `backups`: сведения о резервных копиях.

Связи: `users -> roles`, `news_articles -> news_sources`, `news_articles -> categories`, `logs -> users`, `refresh_tokens -> users`. Добавлены `NOT NULL`, `UNIQUE`, `CHECK`, внешние ключи и индексы.

## Локальный запуск

1. Создайте БД PostgreSQL:

```bash
createdb newsdb
createuser news
psql -c "ALTER USER news WITH PASSWORD 'news';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE newsdb TO news;"
```

2. Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a && source ../.env.example && set +a
alembic upgrade head
uvicorn app.main:app --reload
```

Для Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+psycopg://news:news@localhost:5432/newsdb"
alembic upgrade head
uvicorn app.main:app --reload
```

3. Frontend:

```bash
cd frontend
npm install
npm start
```

Backend: `http://localhost:8000`, Swagger: `http://localhost:8000/docs`, frontend: `http://localhost:4200`.

Администратор создается автоматически: `admin@example.com` / `admin12345`.

## REST API

- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me`
- `GET /api/articles`, `GET /api/categories`, `GET /api/sources`
- `GET/PATCH /api/profile`
- `GET /api/admin/users`, `PATCH /api/admin/users/{id}`, `GET /api/admin/logs`
- `POST/PATCH/DELETE /api/admin/sources`, `POST /api/admin/aggregate`
- `GET/POST /api/admin/backups`, `POST /api/admin/backups/restore`
- `POST /api/admin/migrations`

## Безопасность и администрирование

Пароли хэшируются bcrypt. Валидация входных данных выполняется Pydantic-схемами. Доступ к админским операциям закрыт зависимостью `get_current_admin`. Все SQL-операции проходят через SQLAlchemy ORM. Действия пользователей, ошибки входа, ошибки сервера, агрегация, бэкапы и миграции пишутся в таблицу `logs`.

Резервное копирование:

```bash
DATABASE_URL=postgresql://news:news@localhost:5432/newsdb scripts/backup_db.sh
DATABASE_URL=postgresql://news:news@localhost:5432/newsdb scripts/restore_db.sh backups/backup_YYYYMMDD_HHMMSS.dump
```

PowerShell-версии находятся в `backend/scripts/`.

## Тестирование

```bash
cd backend
pytest
```

Покрыты регистрация, вход, refresh-токены, права доступа, защищенные endpoint-ы, фильтрация ленты, резервное копирование, валидация и наличие обязательных страниц интерфейса с темной темой.

## План практики на 3 недели

| День | Дата | Работа |
|---|---|---|
| 1 | 25.05.2026 | Выбор темы: агрегатор новостей. |
| 2 | 26.05.2026 | Определение структуры приложения. |
| 3 | 27.05.2026 | Выбор стека Angular, FastAPI, PostgreSQL. |
| 4 | 28.05.2026 | Реализация SQL-базы PostgreSQL, таблиц, связей и ограничений. |
| 5 | 29.05.2026 | Настройка SQLAlchemy, Pydantic-схем и конфигурации. |
| 6 | 30.05.2026 | Реализация регистрации, входа, JWT access/refresh. |
| 7 | 31.05.2026 | REST API новостей и RSS-агрегация. |
| 8 | 01.06.2026 | Личный кабинет и административные endpoint-ы. |
| 9 | 02.06.2026 | Логирование действий, ошибок, авторизаций и операций с БД. |
| 10 | 03.06.2026 | Резервное копирование и восстановление через pg_dump/pg_restore. |
| 11 | 04.06.2026 | Механизм обновлений и применения Alembic-миграций. |
| 12 | 05.06.2026 | Каркас Angular и темная тема. |
| 13 | 06.06.2026 | Angular-сервисы, interceptor, auth/admin guard-ы. |
| 14 | 07.06.2026 | Страницы ленты, входа и регистрации. |
| 15 | 08.06.2026 | Личный кабинет и админ-панель. |
| 16 | 09.06.2026 | Тесты авторизации и прав доступа. |
| 17 | 10.06.2026 | Тесты API новостей и резервного копирования. |
| 18 | 11.06.2026 | Тесты безопасности и валидации. |
| 19 | 12.06.2026 | Проверка интерфейса, темной темы и обязательных страниц. |
| 20 | 13.06.2026 | Документация и подготовка демонстрации. |
| 21 | 13.06.2026 | Финальная аттестация, отчеты и контрольный прогон. |

## Коммиты по дням

Скрипт [scripts/create_daily_commits.sh](scripts/create_daily_commits.sh) создает 21 последовательный git-коммит с датами и сообщениями формата `День N: <что сделано>`.
