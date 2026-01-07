from django.http import JsonResponse
from oscar.apps.basket.views import BasketView as CoreBasketView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from oscar.core.loading import get_model

Line = get_model('basket', 'Line')


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
        # Uwaga: Wartości cenowe mogą wymagać ponownego przeliczenia przez strategię,
        # ale w prostym przypadku pobranie ich z właściwości powinno zadziałać,
        # o ile middleware Oscara podpięło strategię do koszyka.

        # Jeśli linia została usunięta, nie możemy odwołać się do jej atrybutów
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
            'items_count': basket.num_lines,
            # Opcjonalnie możesz dodać wiadomości do odpowiedzi JSON, jeśli frontend ma je wyświetlać
            # 'messages': list(flash_messages.values()) if flash_messages else []
        }
        return JsonResponse(data)