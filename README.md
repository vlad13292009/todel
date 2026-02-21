# QuizRumble

[![Pipeline Status](https://gitlab.informatics.ru/2025-2026/vk/s105d/practice/quizrumble/badges/master/pipeline.svg)](https://gitlab.informatics.ru/2025-2026/vk/s105d/practice/quizrumble/-/commits/master)

**Сервис для проведения онлайн‑викторин:** организатор создаёт квиз → участники подключаются по коду/QR → синхронное прохождение → автоматическая статистика.

## Техническое задание

Функциональные требования:

- **Регистрация и вход** — роли: организатор и участник.
- **Вход участника** по уникальному коду или QR‑коду.
- **Создание квиза с вопросами** (P0).
- **Синхронное прохождение сессии** (P0).
- **Автоматический подсчёт баллов и статистика**.
- **Режим «тренировка»** — самопрохождение без ведущего (P0).
- **Импорт/экспорт квизов** в CSV/JSON (P0).

## Технологический стек

**Бэкенд:**
- Python 3.11;
- Django 5.0 + Django ORM;
- Django Channels 4.x (WebSocket, ASGI);
- PostgreSQL 15+ (продакшен), SQLite (разработка);
- Redis 7.x (кэширование, асинхронность).

**Фронтенд:**
- Tailwind CSS 3.x;
- Alpine.js.

**Инфраструктура и инструменты:**
- Docker + docker‑compose;
- pytest, flake8, black, pylint ≥8.0.

## Быстрый старт

### Вариант 1. Через Docker (рекомендуется)

```bash
git clone https://gitlab.informatics.ru/2025-2026/vk/s105d/practice/quizrumble.git
cd quizrumble
docker-compose up --build
```

> Сервис будет доступен по адресу: [http://localhost:8000](http://localhost:8000)

### Вариант 2. Локальный запуск (только для разработки)

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .\.venv\Scripts\activate        # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Структура проекта

```
quizrumble/
├── .gitignore
├── CONTRIBUTING.md               # Правила GitFlow
├── README.md                     # Этот файл
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── patterns.txt                  # Паттерны проектирования
├── logging.conf
├── manage.py
├── quiz_service/                 # Основной Django‑проект
├── accounts/                     # Аутентификация (организатор/участник)
├── quizzes/                      # Управление квизами и вопросами
├── quiz_sessions/                # Сессии, WebSocket, зал ожидания
├── quiz_stat/                    # Статистика и отчёты
├── tests/                        # Тесты (≥30)
└── docs/                         # Документация (Sphinx → GitLab Pages)
```

## Лицензия

Проект разработан в рамках учебного курса МШП. Все права защищены.