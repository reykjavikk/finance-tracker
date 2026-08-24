# Finance Tracker 💰

Веб-приложение для учёта личных финансов на Django 6: категории доходов и расходов,
транзакции, баланс и статистика трат.

## Возможности

- Регистрация и вход (кастомная модель пользователя)
- При регистрации автоматически создаются базовые категории (Зарплата, Фриланс, Продукты, Одежда)
- Учёт транзакций: добавление, редактирование, удаление
- Управление категориями: полный CRUD
- Дашборд: баланс, сумма доходов/расходов, расходы по категориям
- Поиск по транзакциям прямо в интерфейсе
- Кеширование статистики в Redis с автоматической инвалидацией

## Стек технологий

| Слой | Технологии |
|---|---|
| Backend | Python 3.13, Django 6.0 |
| База данных | PostgreSQL 18 |
| Кеш | Redis 7 + django-redis |
| Тесты | pytest, pytest-django |
| Инфраструктура | Docker, docker-compose |

## Быстрый запуск через Docker (рекомендуется)

Понадобится только [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone https://github.com/<username>/finance-tracker.git
cd finance-tracker/myproject
docker compose up --build -d
```

Сайт будет доступен на http://localhost:8000

Создание суперпользователя внутри контейнера:

```bash
docker compose exec web python manage.py createsuperuser
```

## Запуск без Docker

1. Установи PostgreSQL 18 и создай базу:

```sql
CREATE USER finance_user WITH PASSWORD 'твой_пароль' CREATEDB;
CREATE DATABASE finance OWNER finance_user;
```

2. Создай виртуальное окружение и поставь зависимости:

```bash
python -m venv .venv
.venv\Scripts\pip install -r myproject\requirements.txt   # Windows
```

3. Скопируй `.env.example` в `.env` (лежит в папке `myproject`) и заполни своими значениями:

```
SECRET_KEY=свой_случайный_ключ
DEBUG=True
POSTGRES_DB=finance
POSTGRES_USER=finance_user
POSTGRES_PASSWORD=пароль-от-базы
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_URL=
```

4. Примени миграции и запусти сервер:

```bash
cd myproject
..\.venv\Scripts\activate
python manage.py migrate
python manage.py runserver
```

Без `REDIS_URL` кеш работает через встроенный LocMemCache — приложение полностью
функционально и без запущенного Redis.

## Тесты

```bash
python -m pytest -v
```

20 тестов: модели и QuerySet, формы, авторизация, все CRUD-операции
и проверка доступа к чужим данным (ожидается 404).

Перед прогоном pytest пользователю БД нужно право `CREATEDB` — тесты идут
в отдельной базе `test_finance`.

## Структура проекта

```
myproject/
├── manage.py
├── requirements.txt        # зависимости с зафиксированными версиями
├── pytest.ini              # конфигурация тестов
├── conftest.py             # фикстуры pytest
├── Dockerfile              # образ приложения
├── docker-compose.yml      # web + postgres + redis
├── .env.example            # шаблон переменных окружения
├── myproject/
│   └── settings.py         # настройки читаются из env-переменных
└── wallet/
    ├── models.py           # User, Category, Transaction + QuerySet-методы
    ├── views.py            # CRUD, регистрация, дашборд с кешем
    ├── forms.py            # формы транзакций, категорий, регистрации
    ├── urls.py             # маршруты приложения
    ├── middleware.py       # свои middlewares (заголовки, блокировка UA)
    └── tests.py            # автотесты
```
