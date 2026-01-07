from django.shortcuts import render
from django.conf import settings
from oscar.apps.partner.strategy import Selector
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')

def home(request):
    # 1. POBIERANIE Z BAZY
    # Jeśli chcesz 12 produktów, zmień [:8] na [:12]
    db_products = Product.objects.filter(is_public=True).prefetch_related(
        'images',
        'stockrecords'
    ).order_by('-date_created')[:12]

    # Inicjalizacja strategii cenowej
    strategy = Selector().strategy(request=request, user=request.user)

    items = []

    for product in db_products:
        # A. Obliczanie ceny i dostępności za pomocą strategii Oscara
        info = strategy.fetch_for_product(product)

        # --- DOSTĘPNOŚĆ ---
        available_quantity = 0
        if info.availability.is_available_to_buy:
            available_quantity = info.availability.num_available if info.availability.num_available else 0

        # --- CENA ---
        price_val = '0'
        if info.price.is_tax_known:
            price_val = str(info.price.incl_tax)
        else:
            price_val = str(info.price.excl_tax)

        # B. Wyciąganie zdjęcia
        img_obj = product.primary_image()

        if img_obj and img_obj.original:
            image_url = img_obj.original.url
        else:
            image_url = settings.STATIC_URL + 'theme/images/placeholder.png'

        # C. Budowanie słownika
        # WAŻNE: To wcięcie musi być równo z początkiem pętli for (4 spacje wewnątrz pętli),
        # a NIE wewnątrz if-ów powyżej.
        item = {
            "id": str(product.id),
            "name": product.title,
            "image": image_url,
            "price": price_val,
            "quantity": available_quantity,
            "promotion": 'false',
            "discount": '0',
            "discountedPrice": price_val
        }

        items.append(item)

    return render(request, 'home.html', {'items': items})