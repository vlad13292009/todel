```markdown
# Инструкция по запуску тестов QuizRumble

## Требования

- **Количество тестов**: не менее 30
- **Покрытие кода**: не менее 75%
- **Фреймворк**: pytest

---

## Установка зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка тестовых зависимостей
pip install pytest pytest-django pytest-cov coverage
```

---

## Запуск тестов

### Все тесты
```bash
pytest
```

### С покрытием
```bash
pytest --cov=. --cov-report=term
```

### С подробным отчётом
```bash
pytest --cov=. --cov-report=term-missing
```

### Конкретного приложения
```bash
pytest quizzes/tests/
pytest accounts/tests/
```

### Конкретного файла
```bash
pytest quizzes/tests/test_models.py
```

### Конкретного теста
```bash
pytest -k test_quiz_creation
```

### HTML-отчёт
```bash
pytest --cov=. --cov-report=html
# Открыть htmlcov/index.html в браузере
```

### XML-отчёт (для CI/CD)
```bash
pytest --cov=. --cov-report=xml
```

### С минимальным порогом покрытия
```bash
pytest --cov=. --cov-fail-under=75
```

---

## Настройка `pytest.ini`

Создайте файл `pytest.ini` в корне проекта:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = quiz_service.settings
python_files = test_*.py
addopts = --cov=. --cov-report=term --cov-report=xml --cov-report=html
testpaths = quizzes/tests accounts/tests
```

---

## Интерпретация отчётов

### Терминальный отчёт
```text
Name                     Stmts   Miss  Cover
--------------------------------------------
quizzes/models.py          120     15    87%
quizzes/views.py           250     40    84%
--------------------------------------------
TOTAL                      500     57    89%
```

**Расшифровка:**
- `Stmts` — количество операторов в файле
- `Miss` — количество непокрытых операторов
- `Cover` — процент покрытия

### Цвета в HTML-отчёте
| Цвет | Значение |
|------|----------|
| 🟢 Зелёный | Код полностью покрыт тестами |
| 🔴 Красный | Код не покрыт тестами |
| 🟡 Жёлтый | Код частично покрыт |

---

## Пример теста

```python
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from quizzes.models import Quiz

User = get_user_model()

class QuizModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        
    def test_quiz_creation(self):
        """Тест создания викторины"""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            creator=self.user,
            status='draft'
        )
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.status, 'draft')
        self.assertEqual(quiz.creator, self.user)
        
    def test_quiz_str_representation(self):
        """Тест строкового представления"""
        quiz = Quiz.objects.create(
            title='My Quiz',
            creator=self.user
        )
        self.assertEqual(str(quiz), 'My Quiz')
```

---

## Подсчёт количества тестов

```bash
# Посчитать количество тестов
pytest --collect-only -q | grep "test session starts" -A 1000 | grep -c "::<test>"

# Или проще — увидеть сводку после запуска
pytest -q
# Вывод: 32 passed, 2 skipped in 15.42s
```

---

## CI/CD интеграция (GitLab CI пример)

```yaml
# .gitlab-ci.yml
test:
  stage: test
  image: python:3.11
  services:
    - postgres:15-alpine
    - redis:7-alpine
  
  variables:
    POSTGRES_DB: quizrumble_test
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: testpass
    DATABASE_URL: postgres://testuser:testpass@postgres:5432/quizrumble_test
    REDIS_URL: redis://redis:6379/1
  
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-django pytest-cov
  
  script:
    - pytest --cov=. --cov-fail-under=75 --cov-report=xml --cov-report=html
  
  artifacts:
    when: always
    paths:
      - htmlcov/
      - coverage.xml
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

---

## Частые проблемы и решения

| Проблема | Решение |
|----------|---------|
| `no such table: quizzes_quiz` | Добавьте `--create-db` или проверьте миграции: `python manage.py migrate` |
| `collected 0 items` | Убедитесь, что файлы тестов начинаются с `test_` и находятся в `testpaths` |
| `ModuleNotFoundError` | Экспортируйте `PYTHONPATH`: `export PYTHONPATH=$PYTHONPATH:$(pwd)` |
| `Fixture "client" not found` | Убедитесь, что установлен `pytest-django` и настроен `DJANGO_SETTINGS_MODULE` |
| Медленные тесты | Используйте `@pytest.mark.django_db(transaction=True)` только где нужно |
| Утечки БД | Добавьте `@pytest.mark.django_db` и используйте `transaction=False` по умолчанию |

---

## Чеклист перед запуском

- [ ] Виртуальное окружение активировано
- [ ] Зависимости установлены: `pip install -r requirements.txt`
- [ ] База данных создана и миграции применены
- [ ] Файл `.env` настроен для тестового окружения
- [ ] Минимум 30 тестов реализовано
- [ ] Покрытие кода ≥ 75%
- [ ] Все тесты проходят: `pytest` возвращает код 0

---

## Команды для работы с задачей

```bash
git checkout develop && git pull origin develop
git checkout -b feature/qa-64-testing
mkdir -p docs
# скопировать содержимое выше в docs/testing.md
git add docs/testing.md
git commit -m "[#64] Добавлена инструкция по запуску тестов"
git push origin feature/qa-64-testing
```
```
