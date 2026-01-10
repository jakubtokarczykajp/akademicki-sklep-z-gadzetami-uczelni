from django.http import JsonResponse
from oscar.apps.basket.views import BasketView as CoreBasketView
from django.views.decorators.http import require_POST
from oscar.core.loading import get_model
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.http import require_http_methods

Product = get_model('catalogue', 'Product')
Line = get_model('basket', 'Line')


@require_POST
def add_product_to_basket_api(request):
    """
    API endpoint do dodawania produktu do koszyka.
    Przyjmuje product_id i quantity.
    """
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity', 1)
    
    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Brak product_id'}, status=400)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return JsonResponse({'status': 'error', 'message': 'Ilość musi być większa niż 0'}, status=400)
            
        # Pobierz produkt
        product = Product.objects.get(pk=product_id)
        
        # Dodaj do koszyka
        request.basket.add_product(product, quantity=quantity)
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Dodano {quantity} szt. {product.title}',
            'basket_total': str(request.basket.total_incl_tax),
            'basket_count': request.basket.num_items
        })
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produkt nie znaleziony'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Nieprawidłowa ilość'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def update_line_quantity_api(request):
    """
    Prosty endpoint API do aktualizacji ilości w linii koszyka.
    """
    line_id = request.POST.get('line_id')
    quantity = request.POST.get('quantity')

    if not line_id or not quantity:
        return JsonResponse({'status': 'error', 'message': 'Brak danych'}, status=400)

    try:
        # Pobieramy linię należącą do obecnego koszyka
        line = request.basket.lines.get(id=line_id)

        # Konwersja na int
        qty = int(quantity)

        # POPRAWKA: Zamiast nieistniejącej metody update_line, modyfikujemy linię bezpośrednio
        if qty > 0:
            line.quantity = qty
            line.save()
        else:
            # Jeśli ilość <= 0, usuwamy linię z koszyka
            line.delete()

        # Zwracamy nowe dane
        if qty > 0:
            line_price = str(line.line_price_incl_tax)
            new_quantity = line.quantity
            line_id_resp = line.id
        else:
            line_price = "0.00"
            new_quantity = 0
            line_id_resp = None

        return JsonResponse({
            'status': 'ok',
            'line_id': line_id_resp,
            'new_quantity': new_quantity,
            'line_price': line_price,
            'basket_total': str(request.basket.total_incl_tax)
        })

    except Line.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Linia nie znaleziona'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Nieprawidłowa ilość'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(vary_on_headers('X-Requested-With'), name='dispatch')
class BasketSummaryView(CoreBasketView):
    def render_to_response(self, context, **response_kwargs):
        # Sprawdzamy czy to żądanie AJAX
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Przekazujemy wszystkie argumenty (np. formset) dalej
            return self.json_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    # POPRAWKA: Dodajemy 'flash_messages=None' jako argument, aby obsłużyć wywołanie z formset_valid
    def json_response(self, context, flash_messages=None, **kwargs):
        basket = self.request.basket
        items = []
        for line in basket.all_lines():
            # Upewnij się, że zdjęcie istnieje, zanim spróbujesz pobrać URL
            image_url = ''
            product_image = line.product.primary_image()
            if product_image:
                image_url = product_image.original.url

            items.append({
                'id': line.product.id,
                'name': line.product.title,
                'quantity': line.quantity,
                'price': str(line.unit_price_incl_tax),
                'image': image_url,
                'total': str(line.line_price_incl_tax),
                'line_id': line.id,
            })

        data = {
            'products': items,
            'total_price': str(basket.total_incl_tax),
            'items_count': basket.num_items,
        }
        response = JsonResponse(data)
     
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


def get_user_wishlists_api(request):
    """
    AJAX endpoint do pobierania wishlistów zalogowanego użytkownika.
    Zwraca JSON z listą wishlistów.
    """
    try:
        # Najpierw sprawdzamy czy użytkownik jest zalogowany
        if not request.user.is_authenticated:
            return JsonResponse({'wishlists': [], 'authenticated': False}, status=200)
        
        # Ładujemy WishList model za pomocą Oscar loadera
        from oscar.core.loading import get_model
        WishList = get_model('wishlists', 'WishList')
        
        # Pobierz wishlists zalogowanego użytkownika
        wishlists = WishList.objects.filter(owner=request.user)
        
        wishlists_list = []
        for wishlist in wishlists:
            wishlists_list.append({
                'id': wishlist.id,
                'key': wishlist.key,
                'name': wishlist.name,
            })
        
        return JsonResponse({'wishlists': wishlists_list, 'authenticated': True}, status=200)
        
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        error_trace = traceback.format_exc()
        print(f"Error in get_user_wishlists_api:\n{error_msg}\n{error_trace}")
        # Zwracamy 200 z informacją o błędzie zamiast 500
        return JsonResponse({
            'wishlists': [], 
            'error': error_msg,
            'authenticated': request.user.is_authenticated
        }, status=200)


@require_http_methods(["POST"])
def add_product_to_wishlist_api(request):
    """
    Endpoint API do dodawania produktu do wishlista.
    Parametry: wishlist_id, product_id
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Nie jesteś zalogowany'}, status=401)
    
    try:
        wishlist_id = request.POST.get('wishlist_id')
        product_id = request.POST.get('product_id')
        
        if not wishlist_id or not product_id:
            return JsonResponse({'status': 'error', 'message': 'Brak parametrów'}, status=400)
        
        # Ładujemy modele
        WishList = get_model('wishlists', 'WishList')
        Product = get_model('catalogue', 'Product')
        Line = get_model('wishlists', 'Line')
        
        # Pobierz wishlist i sprawdź czy należy do użytkownika
        wishlist = WishList.objects.get(id=wishlist_id, owner=request.user)
        
        # Pobierz produkt
        product = Product.objects.get(id=product_id)
        
        # Sprawdzamy czy produkt już jest na liście
        line, created = Line.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Produkt został dodany do listy życzeń',
            'product_id': product_id,
            'wishlist_id': wishlist_id
        }, status=200)
        
    except WishList.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Lista życzeń nie znaleziona'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produkt nie znaleziony'}, status=404)
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        error_trace = traceback.format_exc()
        print(f"Error in add_product_to_wishlist_api:\n{error_msg}\n{error_trace}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=200)

