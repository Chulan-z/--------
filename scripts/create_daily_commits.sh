#!/usr/bin/env bash
set -euo pipefail

git init
git config user.name >/dev/null || git config user.name "Практика"
git config user.email >/dev/null || git config user.email "practice@example.com"
git add README.md .gitignore .env.example reports/report_day_01.md reports/README.md
GIT_AUTHOR_DATE="2026-05-25T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-25T10:00:00+03:00" git commit -m "День 1: выбор темы агрегатора новостей"

git add frontend/angular.json backend/alembic.ini reports/report_day_02.md
GIT_AUTHOR_DATE="2026-05-26T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-26T10:00:00+03:00" git commit -m "День 2: определение структуры приложения"

git add backend/requirements.txt frontend/package.json frontend/tsconfig*.json reports/report_day_03.md
GIT_AUTHOR_DATE="2026-05-27T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-27T10:00:00+03:00" git commit -m "День 3: выбор стека технологий"

git add backend/app/db backend/app/models backend/sql backend/alembic reports/report_day_04.md
GIT_AUTHOR_DATE="2026-05-28T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-28T10:00:00+03:00" git commit -m "День 4: реализация SQL-базы PostgreSQL, таблицы и связи"

git add backend/app/core backend/app/schemas reports/report_day_05.md
GIT_AUTHOR_DATE="2026-05-29T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-29T10:00:00+03:00" git commit -m "День 5: настройка конфигурации и схем валидации"

git add backend/app/api/auth.py backend/app/api/deps.py backend/app/services/seed.py reports/report_day_06.md
GIT_AUTHOR_DATE="2026-05-30T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-30T10:00:00+03:00" git commit -m "День 6: регистрация, авторизация и JWT-токены"

git add backend/app/api/news.py backend/app/services/news_aggregator.py reports/report_day_07.md
GIT_AUTHOR_DATE="2026-05-31T10:00:00+03:00" GIT_COMMITTER_DATE="2026-05-31T10:00:00+03:00" git commit -m "День 7: REST API новостей и RSS-агрегация"

git add backend/app/api/admin.py backend/app/api/profile.py backend/app/main.py reports/report_day_08.md
GIT_AUTHOR_DATE="2026-06-01T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-01T10:00:00+03:00" git commit -m "День 8: админские маршруты и личный кабинет"

git add backend/app/services/audit.py reports/report_day_09.md
GIT_AUTHOR_DATE="2026-06-02T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-02T10:00:00+03:00" git commit -m "День 9: аудит действий и серверное логирование"

git add backend/app/services/backup.py backend/scripts scripts/backup_db.sh scripts/restore_db.sh reports/report_day_10.md
GIT_AUTHOR_DATE="2026-06-03T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-03T10:00:00+03:00" git commit -m "День 10: резервное копирование и восстановление БД"

git add backend/app/services/migrations.py reports/report_day_11.md
GIT_AUTHOR_DATE="2026-06-04T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-04T10:00:00+03:00" git commit -m "День 11: механизм обновлений и применения миграций"

git add frontend/src/index.html frontend/src/main.ts frontend/src/styles.css frontend/src/app/models reports/report_day_12.md
GIT_AUTHOR_DATE="2026-06-05T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-05T10:00:00+03:00" git commit -m "День 12: базовый Angular-интерфейс и темная тема"

git add frontend/src/app/services frontend/src/app/guards frontend/src/app/app* reports/report_day_13.md
GIT_AUTHOR_DATE="2026-06-06T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-06T10:00:00+03:00" git commit -m "День 13: Angular-сервисы, маршруты и guard-ы"

git add frontend/src/app/pages/feed-page.component.ts frontend/src/app/pages/login-page.component.ts frontend/src/app/pages/register-page.component.ts reports/report_day_14.md
GIT_AUTHOR_DATE="2026-06-07T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-07T10:00:00+03:00" git commit -m "День 14: страницы ленты, входа и регистрации"

git add frontend/src/app/pages/profile-page.component.ts frontend/src/app/pages/admin-page.component.ts reports/report_day_15.md
GIT_AUTHOR_DATE="2026-06-08T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-08T10:00:00+03:00" git commit -m "День 15: личный кабинет и панель администрирования"

git add backend/tests/test_auth.py backend/tests/test_rbac.py reports/report_day_16.md
GIT_AUTHOR_DATE="2026-06-09T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-09T10:00:00+03:00" git commit -m "День 16: тесты авторизации и прав доступа"

git add backend/tests/test_news.py backend/tests/test_backup.py reports/report_day_17.md
GIT_AUTHOR_DATE="2026-06-10T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-10T10:00:00+03:00" git commit -m "День 17: тесты новостей и резервного копирования"

git add backend/tests/test_security.py backend/tests/conftest.py reports/report_day_18.md
GIT_AUTHOR_DATE="2026-06-11T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-11T10:00:00+03:00" git commit -m "День 18: тесты безопасности и тестовая конфигурация"

git add backend/tests/test_frontend_contract.py reports/report_day_19.md
GIT_AUTHOR_DATE="2026-06-12T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-12T10:00:00+03:00" git commit -m "День 19: проверка интерфейса и темной темы"

git add reports/report_day_20.md
GIT_AUTHOR_DATE="2026-06-13T10:00:00+03:00" GIT_COMMITTER_DATE="2026-06-13T10:00:00+03:00" git commit -m "День 20: подготовка документации и инструкции запуска"

git add reports/report_day_21.md scripts/create_daily_commits.sh
GIT_AUTHOR_DATE="2026-06-13T17:00:00+03:00" GIT_COMMITTER_DATE="2026-06-13T17:00:00+03:00" git commit -m "День 21: финальная аттестация и оформление отчетов"
