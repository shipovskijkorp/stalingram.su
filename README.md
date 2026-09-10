# Stalingram

Мессенджер с интерфейсом в советской стилистике и небольшими тематическими пасхалками.

## Структура

- `config/` — настройки Django, ASGI/WSGI и корневые URL.
- `apps/accounts/` — пользователи, регистрация, авторизация и профили.
- `apps/messenger/` — интерфейс и будущая логика чатов.
- `templates/` — HTML-шаблоны.
- `static/` — CSS и JavaScript.
- `var/` — локальная база, собранная статика и пользовательские файлы; не коммитится.
- `deploy/` — заготовки для Nginx и systemd на VPS.

## Локальный запуск

Требуется Python 3.11+.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py manage.py migrate
py manage.py runserver
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

После запуска:

- `http://127.0.0.1:8000/register/` — регистрация;
- `http://127.0.0.1:8000/login/` — вход;
- `http://127.0.0.1:8000/` — мессенджер после авторизации;
- `http://127.0.0.1:8000/profile/` — настройки собственного профиля;
- `http://127.0.0.1:8000/u/<username>/` — публичный профиль пользователя.

Почта сейчас не подтверждается. Для входа можно использовать логин или почту вместе с паролем. В публичном профиле почта не отображается.

Профиль поддерживает имя и фамилию, уникальное имя пользователя, описание до 160 символов, фотографию профиля и смену пароля. Фотографии хранятся в `var/media/avatars/`; локально Django отдаёт их сам, а на VPS для `/media/` уже предусмотрен Nginx.

## Перенос на VPS

Локально используется SQLite, поэтому для разработки отдельный сервер БД не нужен. На VPS предусмотрен PostgreSQL без изменения кода приложения.

1. Установить зависимости из `requirements-production.txt`.
2. Скопировать `.env.example` в `.env` и выставить как минимум:

```env
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_ALLOWED_HOSTS=stalingram.su,www.stalingram.su
DJANGO_CSRF_TRUSTED_ORIGINS=https://stalingram.su,https://www.stalingram.su
DB_ENGINE=postgresql
POSTGRES_DB=stalingram
POSTGRES_USER=stalingram
POSTGRES_PASSWORD=replace-me
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

3. Выполнить:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

4. Адаптировать пути и пользователя в `deploy/systemd/stalingram.service`, установить unit.
5. Установить конфиг из `deploy/nginx/stalingram.conf`, затем подключить HTTPS.

Приложение слушает локальный `127.0.0.1:8000`, а наружу на VPS его отдаёт Nginx. Поэтому локальная разработка и сервер используют одну и ту же Django-структуру; меняется только окружение и база данных.
