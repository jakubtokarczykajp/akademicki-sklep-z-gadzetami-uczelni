# Instruckja

## Uruchamianie projektu (DEV)
### Windows
```shell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
npm run dev
```
### Linux

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
npm run dev
```

## W przypadku gdy nie ma dostępnych krajów dostawy
```shell
python manage.py oscar_populate_countries
```

## Przy problemie z wyświetlaniem/wyszukiwaniem produktów
```shell
python manage.py rebuild_index --noinput
```

## Dostęp do panelu administracyjnego
Tworzenie użytkownika z dostępem

```shell
python manage.py createsuperuser
```
## Testy

```shell
python manage.py test
```