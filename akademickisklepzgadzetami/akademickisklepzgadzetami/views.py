from django.shortcuts import render
from oscar.core.loading import get_model
Product = get_model('catalogue', 'Product')


def home(request):
    # 1. POBIERANIE Z BAZY
    # Pobieramy produkty z bazy danych (np. 8 najnowszych)
    db_products = Product.objects.filter(is_public=True).prefetch_related(
        'images',
        'stockrecords'
    ).order_by('-date_created')[:8]

    # 2. KONWERSJA (MAPOWANIE)
    # Tworzymy pustą listę, do której wrzucimy "przetłumaczone" produkty
    items = []

    for product in db_products:
        # A. Wyciąganie zdjęcia
        # Domyślna ścieżka, jeśli produkt nie ma zdjęcia
        image_url = 'theme/images/placeholder.png'
        img_obj = product.primary_image()
        if img_obj and img_obj.original:
            # .url zwraca np. /media/images/products/...
            image_url = img_obj.original.url

        # B. Wyciąganie ceny
        price = '0'
        # Pobieramy pierwszy wpis magazynowy (tam jest cena w prostym setupie Oscara)
        stock = product.stockrecords.first()
        if stock and stock.price:
            # Konwertujemy Decimal na string, np. "120.00"
            price = str(stock.price)

        # C. Budowanie słownika w Twoim formacie
        item = {
            "id": str(product.id),
            "name": product.title,
            "image": image_url,
            "price": price,

            # Pola promocyjne - na razie ustawiamy "na sztywno"
            # (Oscar ma skomplikowany system promocji, to jest wersja uproszczona)
            "promotion": 'false',
            "discount": '0',
            "discountedPrice": price  # Domyślnie cena promocyjna to cena zwykła
        }

        # Dodajemy gotowy słownik do listy
        items.append(item)

    # 3. WYSŁANIE DO SZABLONU
    return render(request, 'home.html', {'items': items})