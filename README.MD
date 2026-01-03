# Uruchamianie projektu (DEV)
## Windows
```shell
python -m venv venv

.\.venv\Scripts\activate

pip install -r requirements.txt

# TODO: dodać do requirements?
pip install django-tailwind
pip install sorl-thumbnail
pip install django-browser-reload
pip install pysolr

python manage.py migrate
python manage.py runserver

npm run dev
```

## Dostęp do panelu administracyjnego
Tworzenie użytkownika z dostępem

```shell
python manage.py createsuperuser
```