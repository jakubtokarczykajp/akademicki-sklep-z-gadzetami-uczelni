from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.checkout.views import PaymentMethodView as CorePaymentMethodView
from oscar.apps.payment.models import SourceType, Source
from oscar.apps.order.models import PaymentEventType
from oscar.core.loading import get_model
from django.shortcuts import redirect
from django.urls import reverse
import logging

Order = get_model('order', 'Order')
logger = logging.getLogger(__name__)


class PaymentMethodView(CorePaymentMethodView):
    def dispatch(self, request, *args, **kwargs):
        return redirect(reverse('checkout:preview'))


class PaymentDetailsView(CorePaymentDetailsView):

    def get_order_number(self):
        """
        Pobiera numer zamówienia. Jeśli standardowy numer jest zajęty,
        dodaje sufiks (np. -1, -2), aby znaleźć wolny numer.
        """
        order_number = super().get_order_number()

        if not Order.objects.filter(number=order_number).exists():
            return order_number

        # Jeśli numer zajęty, szukamy wolnego z sufiksem
        i = 1
        while True:
            new_number = f"{order_number}-{i}"
            if not Order.objects.filter(number=new_number).exists():
                return new_number
            i += 1

    def handle_payment(self, order_number, total, **kwargs):
        try:
            source_type, _ = SourceType.objects.get_or_create(
                name='Płatność Testowa',
                defaults={'code': 'test-payment'}
            )

            source = Source(
                source_type=source_type,
                currency=total.currency,
                amount_allocated=total.incl_tax,
                amount_debited=total.incl_tax,
            )
            self.add_payment_source(source)

            event_type, _ = PaymentEventType.objects.get_or_create(
                name='Opłacono',
                defaults={'code': 'paid'}
            )

            self.add_payment_event(event_type.name, total.incl_tax)

        except Exception as e:
            logger.exception("BŁĄD PŁATNOŚCI W CHECKOUT:")
            raise e

    def submit(self, user, basket, shipping_address, shipping_method,
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None, **kwargs):

        return super().submit(user, basket, shipping_address, shipping_method,
                              shipping_charge, billing_address, order_total,
                              payment_kwargs=payment_kwargs,
                              order_kwargs=order_kwargs,
                              **kwargs)