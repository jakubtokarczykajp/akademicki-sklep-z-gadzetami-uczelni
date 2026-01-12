from decimal import Decimal
from django.test import TestCase
from oscar.core.loading import get_model, get_class

Basket = get_model('basket', 'Basket')
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Strategy = get_class('partner.strategy', 'Default')

class BasketModelTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(name="Clothing")
        self.product = Product.objects.create(title="T-shirt", product_class=self.product_class)
        self.product2 = Product.objects.create(title="Hoodie", product_class=self.product_class)
        self.partner = Partner.objects.create(name="Test Partner")
        StockRecord.objects.create(
            product=self.product, partner=self.partner, partner_sku='TSHIRT01',
            price=Decimal("10.00"), num_in_stock=100
        )
        StockRecord.objects.create(
            product=self.product2, partner=self.partner, partner_sku='HOODIE01',
            price=Decimal("25.00"), num_in_stock=50
        )
        self.strategy = Strategy()

    def _get_basket(self):
        basket = Basket.objects.create()
        basket.strategy = self.strategy
        return basket

    def test_basket_creation(self):
        basket = self._get_basket()
        self.assertIsNotNone(basket.pk)

    def test_add_product_to_basket(self):
        basket = self._get_basket()
        basket.add_product(self.product)
        self.assertEqual(basket.lines.count(), 1)
        line = basket.lines.first()
        self.assertEqual(line.product, self.product)
        self.assertEqual(line.quantity, 1)

    def test_add_same_product_updates_quantity(self):
        basket = self._get_basket()
        basket.add_product(self.product, quantity=1)
        basket.add_product(self.product, quantity=2)
        self.assertEqual(basket.lines.count(), 1)
        self.assertEqual(basket.lines.first().quantity, 3)

    def test_basket_total_price(self):
        basket = self._get_basket()
        basket.add_product(self.product, quantity=2)
        self.assertEqual(basket.total_excl_tax, Decimal("20.00"))
        self.assertEqual(basket.total_incl_tax, Decimal("20.00"))

    def test_add_multiple_different_products(self):
        basket = self._get_basket()
        basket.add_product(self.product, quantity=1)
        basket.add_product(self.product2, quantity=2)
        self.assertEqual(basket.lines.count(), 2)
        self.assertEqual(basket.num_items, 3)
        self.assertEqual(basket.total_excl_tax, Decimal("10.00") + Decimal("50.00"))

    def test_update_line_quantity_with_delta(self):
        """
        Tests updating a line's quantity by passing a delta to add_product.
        This is the correct way to set a specific quantity on a line.
        """
        basket = self._get_basket()
        # Add 5 initially
        basket.add_product(self.product, quantity=5)
        self.assertEqual(basket.lines.first().quantity, 5)
        self.assertEqual(basket.total_excl_tax, Decimal("50.00"))
        
        # To change the quantity from 5 to 3, we must pass a delta of -2.
        current_qty = basket.lines.first().quantity
        new_qty = 3
        delta = new_qty - current_qty
        basket.add_product(self.product, quantity=delta)
        
        self.assertEqual(basket.lines.count(), 1)
        self.assertEqual(basket.lines.first().quantity, 3)
        self.assertEqual(basket.total_excl_tax, Decimal("30.00"))

    def test_flush_basket(self):
        basket = self._get_basket()
        basket.add_product(self.product, quantity=5)
        self.assertFalse(basket.is_empty)
        basket.flush()
        self.assertTrue(basket.is_empty)
        self.assertEqual(basket.lines.count(), 0)
