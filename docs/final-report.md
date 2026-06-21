# Mood Journal — Финальный отчет

## 1. Описание проекта

Mood Journal — веб-приложение для отслеживания настроения. Пользователь каждый день записывает свое настроение по шкале от 1 до 5 и может добавить заметку. Потом можно посмотреть статистику и историю за любой период.

### Основные функции

- Запись настроения (1-5) с текстовой заметкой
- Просмотр истории записей за выбранный период
- Статистика: среднее настроение, количество записей по категориям
- Удаление записей
- Визуализация: календарь-heatmap и диаграммы

## 2. Архитектура

Приложение построено по классической клиент-серверной схеме:

```
┌─────────────────┐
│    Frontend     │
│ HTML/CSS/JS     │
│ Chart.js        │
└────────┬────────┘
         │ REST API (JSON)
         v
┌─────────────────┐
│    Backend      │
│ Python/FastAPI  │
│ SQLAlchemy ORM  │
└────────┬────────┘
         │ SQL
         v
┌─────────────────┐
│   SQLite DB     │
│ mood_journal.db │
└─────────────────┘
```

### Структура проекта

```
mood-journal/
├── backend/
│   ├── main.py           — точка входа, создание приложения FastAPI
│   ├── database.py       — подключение к SQLite через SQLAlchemy
│   ├── models.py         — ORM-модель MoodEntry
│   ├── schemas.py        — Pydantic-схемы для валидации
│   ├── routers/
│   │   └── entries.py    — все API-эндпоинты
│   └── requirements.txt  — зависимости Python
├── frontend/
│   ├── index.html        — главная страница
│   ├── css/style.css     — стили
│   └── js/
│       ├── app.js        — логика взаимодействия с API
│       └── charts.js     — графики и heatmap
├── tests/
│   ├── test_api.py       — API-тесты (TestClient)
│   └── test_models.py    — unit-тесты моделей и схем
├── docs/
│   ├── security-report.md — отчет SAST
│   ├── sca-report.md      — отчет SCA + SBOM
│   └── final-report.md    — этот документ
├── .github/workflows/
│   └── ci.yml            — CI pipeline (7 jobs)
├── Dockerfile            — сборка контейнера
├── docker-compose.yml    — запуск через compose
├── pyproject.toml        — конфиг Ruff
└── README.md
```

## 3. API

Базовый URL: `http://localhost:8000`

Swagger-документация: `http://localhost:8000/docs`

### Эндпоинты

| Метод | URL | Описание | Тело запроса | Ответ |
|---|---|---|---|---|
| POST | /api/entries/ | Создать запись | `{"mood": 4, "note": "хороший день"}` | 201 + объект записи |
| GET | /api/entries/?days=30 | Список записей за N дней | — | 200 + массив записей |
| GET | /api/entries/stats?days=30 | Статистика за N дней | — | 200 + объект статистики |
| DELETE | /api/entries/{id} | Удалить запись | — | 204 |

### Модель данных

```
MoodEntry:
  id         — int, автоинкремент, первичный ключ
  mood       — int, от 1 до 5 (1=ужасно, 5=отлично)
  note       — text, до 1000 символов, необязательно
  created_at — datetime, автоматически при создании
```

### Примеры запросов

Создание записи:
```bash
curl -X POST http://localhost:8000/api/entries/ \
  -H "Content-Type: application/json" \
  -d '{"mood": 4, "note": "сегодня нормально"}'
```

Получение статистики:
```bash
curl http://localhost:8000/api/entries/stats?days=7
```

Ответ:
```json
{
  "total_entries": 5,
  "average_mood": 3.6,
  "mood_counts": {"3": 2, "4": 2, "5": 1}
}
```

## 4. Тестирование

### Типы тестов

**Unit-тесты** (test_models.py, 8 тестов):
- Создание модели MoodEntry
- Валидация Pydantic-схем (mood 1-5, note <= 1000 символов)
- Проверка значений по умолчанию
- Проверка невалидных данных

**API-тесты** (test_api.py, 9 тестов):
- CRUD операции через TestClient
- Тестовая SQLite-база (test.db) чтобы не трогать основную
- Проверка кодов ответа (201, 200, 204, 404, 422)
- Проверка статистики

### Запуск тестов

```bash
# из корня проекта
set PYTHONPATH=backend
python -m pytest tests/ -v
```

Результат:
```
tests/test_api.py::test_create_entry PASSED
tests/test_api.py::test_create_entry_without_note PASSED
tests/test_api.py::test_create_entry_invalid_mood PASSED
tests/test_api.py::test_list_entries PASSED
tests/test_api.py::test_list_entries_empty PASSED
tests/test_api.py::test_get_stats PASSED
tests/test_api.py::test_get_stats_empty PASSED
tests/test_api.py::test_delete_entry PASSED
tests/test_api.py::test_delete_nonexistent PASSED
tests/test_models.py::test_mood_entry_creation PASSED
tests/test_models.py::test_entry_create_schema_valid PASSED
tests/test_models.py::test_entry_create_schema_defaults PASSED
tests/test_models.py::test_entry_create_schema_invalid_mood PASSED
tests/test_models.py::test_entry_create_schema_long_note PASSED
tests/test_models.py::test_entry_response_schema PASSED
tests/test_models.py::test_stats_response_empty PASSED
tests/test_models.py::test_stats_response_with_data PASSED

17 passed
```

## 5. CI/CD Pipeline

GitHub Actions pipeline запускается при каждом PR в main и при push в main.

### Jobs (7 штук)

| Job | Что делает |
|---|---|
| Lint & Format | Ruff — проверка стиля кода и форматирования |
| Build & Check | Проверка что приложение импортируется без ошибок |
| Tests | Запуск pytest (17 тестов) |
| Semgrep SAST | Статический анализ безопасности кода |
| Bandit Security | Python-специфичный анализ безопасности |
| SCA - Dependency Audit | pip-audit — проверка зависимостей на CVE |
| Trivy Container Scan | Сканирование Docker-образа на уязвимости |

Branch protection настроен — merge в main заблокирован пока CI не пройдет.

## 6. Docker

### Dockerfile

Используется `python:3.12-slim` — минимальный образ (~150 МБ вместо ~900 МБ у полного).

Оптимизации:
- Зависимости копируются отдельным слоем (кэшируются при пересборке)
- `--no-cache-dir` при pip install (меньше размер образа)
- `.dockerignore` исключает git, кэши, базу данных

### Запуск

```bash
docker build -t mood-journal .
docker run -p 8000:8000 mood-journal

# или через compose
docker-compose up --build
```

## 7. Безопасность

### SAST (Static Application Security Testing)

Инструменты: Semgrep, Bandit

Результат: 0 уязвимостей найдено

Почему код безопасен:
- ORM вместо сырого SQL — защита от SQL-инъекций
- Pydantic валидирует все входные данные
- Нет хардкод-паролей и секретов
- Нет eval/exec

Подробный отчет: `docs/security-report.md`

### SCA (Software Composition Analysis)

Инструменты: pip-audit, Trivy

Результат: 23 зависимости проверены, 0 уязвимостей

SBOM (список всех зависимостей с версиями) доступен в `docs/sca-report.md`

## 8. Этапы разработки

| Этап | Что сделано | PR |
|---|---|---|
| ДЗ 1 | Репозиторий + README с описанием проекта | #1 |
| ДЗ 2 | Работающее приложение (backend + frontend) | #1 |
| ДЗ 3 | CI pipeline — Ruff линтер + проверки | #2 |
| ДЗ 4 | Docker — Dockerfile + docker-compose | #3 |
| ДЗ 5 | Тесты — unit (8) + API (9) = 17 тестов | #4 |
| ДЗ 6 | SAST — Semgrep + Bandit в CI | #5 |
| ДЗ 7 | SCA — pip-audit + Trivy, SBOM | #6 |
| ДЗ 8 | Финальная документация | #7 |

## 9. Как развернуть проект с нуля

### Вариант 1: Локально

```bash
git clone https://github.com/TohaProLife/mood-journal.git
cd mood-journal/backend

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
uvicorn main:app --reload
```

Приложение: http://localhost:8000
API-документация: http://localhost:8000/docs

### Вариант 2: Docker

```bash
git clone https://github.com/TohaProLife/mood-journal.git
cd mood-journal
docker-compose up --build
```

### Запуск тестов

```bash
set PYTHONPATH=backend
python -m pytest tests/ -v
```

## 10. Что можно улучшить

- Добавить авторизацию (JWT)
- Перейти с SQLite на PostgreSQL для продакшена
- Добавить CORS-настройки
- Вынести конфиг БД в переменные окружения
- Добавить теги для фильтрации записей
- Сделать мобильную версию
- Настроить Dependabot для автоматических обновлений зависимостей
