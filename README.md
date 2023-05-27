![example workflow](https://github.com/samec2011/naizi/actions/workflows/naizi_workflow.yml/badge.svg)
# На-изи, это социальная сеть, помогающая вкусно и полезно готовить еду. 
### Технологии
Python 3.7, Django 3.2, DRF, Djoser, Docker, Nginx, PostgreSQL

## О проекте
* На-изи - это социальная сеть для размещения рецептов различных блюд, где пользователи могут делиться своими кулинарными находками, открывать новые вкусы и общаться друг с другом. Здесь можно найти множество интересных рецептов, советов от профессиональных поваров и любителей кулинарии. С помощью На-изи вы можете легко и удобно найти идеи для ежедневных и праздничных блюд, собрать свою личную книгу рецептов и делиться своими кулинарными экспериментами с другими.
  
### Шаблон env-файла 
```bash
DB_ENGINE=django.db.backends.postgresql - указываем, что используется PostgreSql
DB_NAME=имя базы данных
POSTGRES_USER=имя пользователя БД
POSTGRES_PASSWORD=пароль пользователя БД
DB_HOST=db - хост БД
DB_PORT=5432 - порт подключения к БД
SECRET_KEY=super-secret-key из settings.py
```
### Описание команд для запуска приложения в контейнерах
```bash
sudo docker compose up -d --build
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py createsuperuser
sudo docker compose exec backend python manage.py collectstatic --no-input
```
### Описание команды для заполнения базы данными
```bash
sudo docker compose exec backend python manage.py importcsv --filename 'ingredients.csv' --model_name 'Ingredient'
sudo docker compose exec backend python manage.py importcsv --filename 'tags.csv' --model_name 'Tag'
sudo docker compose exec backend python manage.py loaddata fixtures.json
```

## Авторы
* [Потапов  Юра](https://github.com/samec2011)
## Проект доступен по ссылке
* [сайт na-izi.com](http://na-izi.com/)