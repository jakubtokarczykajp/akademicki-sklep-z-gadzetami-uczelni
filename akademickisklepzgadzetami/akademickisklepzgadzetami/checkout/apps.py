from oscar.apps.checkout.apps import CheckoutConfig as CoreCheckoutConfig
from oscar.core.loading import get_class

class CheckoutConfig(CoreCheckoutConfig):
    name = 'akademickisklepzgadzetami.checkout'

    def ready(self):
        super().ready()
        # Podmieniamy widoki na nasze wersje
        self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')
        self.payment_method_view = get_class('checkout.views', 'PaymentMethodView')