from oscar.apps.basket.apps import BasketConfig as CoreBasketConfig
from oscar.core.loading import get_class


class BasketConfig(CoreBasketConfig):
    name = 'akademickisklepzgadzetami.basket'

    def ready(self):
        super().ready()
        self.summary_view = get_class('basket.views', 'BasketSummaryView')