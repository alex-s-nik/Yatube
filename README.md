# Yatube
### Описание
Yatube - социальная сеть блогеров. Она даёт пользователям возможность создать учётную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.
### Технологии
Python 3.7
Django 2.2.19
### Запуск проекта в dev-режиме
Для запуска проекта необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/RussianPostman/api_yamdb.git
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv        (для *nix-систем)
source venv/bin/activate    (для *nix-систем)
```

```
python -m venv venv         (для Windows-систем)
env/Scripts/activate.bat    (для Windows-систем)
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip    (для *nix-систем)
python -m pip install --upgrade pip     (для Windows-систем)
```
```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate   (для *nix-систем)
python manage.py migrate    (для Windows-систем)
```

Запустить проект:

```
python3 manage.py runserver (для *nix-систем)
python manage.py runserver  (для Windows-систем)
```

Перейти в браузере по адресу

```
http://127.0.0.1:8000
```

### Автор
alex-s-nik
