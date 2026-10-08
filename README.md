# Сервис управления рассылками

Веб-приложение на Django для управления email-рассылками: создание получателей, сообщений, рассылок, отправка писем, статистика, аутентификация, роли и кеширование.

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Скопировать .env.example -> .env и заполнить
cp .env.example .env

# 3. Применить миграции
python manage.py migrate

# 4. Создать суперпользователя
python manage.py createsuperuser

# 5. Запустить сервер
python manage.py runserver
```

## Структура проекта

- `config/` — настройки Django (settings, urls, wsgi, asgi)
- `mailing/` — основное приложение (модели, формы, views, сервис отправки)
- `users/` — приложение пользователей (регистрация, вход, профиль, роли)
- `templates/` — HTML-шаблоны
- `static/` — статика

## Модели

| Модель | Описание |
|--------|----------|
| `Recipient` | Получатель рассылки (email, ФИО, комментарий, владелец) |
| `Message` | Сообщение (тема, тело, владелец) |
| `Mailing` | Рассылка (start_time, end_time, message, recipients, is_disabled) |
| `Attempt` | Попытка отправки (время, статус, ответ сервера, mailing) |

## Роли

- **Пользователь** — управляет своими рассылками, получателями, сообщениями
- **Менеджер** (`is_manager=True`) — видит все рассылки/получателей, может блокировать пользователей и отключать рассылки

## Команды

```bash
# Отправка активных рассылок
python manage.py send_mailings
```

## Кеширование

- **Серверное**: Redis (настраивается в .env), кеширование главной страницы и статистики (60 сек)
- **Клиентское**: middleware `UpdateCacheMiddleware` / `FetchFromCacheMiddleware`

## Настройка email

Заполните в `.env`:
```
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_SSL=True
```

Для тестирования без реальной отправки замените backend в settings.py:
```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```
