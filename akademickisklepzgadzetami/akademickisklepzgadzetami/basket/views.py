from django.http import JsonResponse
from oscar.apps.basket.views import BasketView as CoreBasketView

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