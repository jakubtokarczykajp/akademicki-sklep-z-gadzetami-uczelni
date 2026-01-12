from decimal import Decimal
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model, get_class
from oscar.apps.checkout.calculators import OrderTotalCalculator

# Correctly load all necessary models and classes
User = get_user_model()
Order = get_model('order', 'Order')
Basket = get_model('basket', 'Basket')
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
OrderCreator = get_class('order.utils', 'OrderCreator')
Strategy = get_class('partner.strategy', 'Default')
ShippingAddress = get_model('order', 'ShippingAddress')
BillingAddress = get_model('order', 'BillingAddress')
Country = get_model('address', 'Country')
Free = get_class('shipping.methods', 'Free')

class UniversityCheckoutTransactionTest(TransactionTestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(name="University Gadgets")
        self.mug = Product.objects.create(title="University Mug", product_class=self.product_class)
        self.hoodie = Product.objects.create(title="University Hoodie", product_class=self.product_class)
        
        self.partner = Partner.objects.create(name="University Store")
        self.mug_stock = StockRecord.objects.create(
            product=self.mug, partner=self.partner, partner_sku="MUG01", 
            price=Decimal("15.00"), num_in_stock=50, num_allocated=0
        )
        self.hoodie_stock = StockRecord.objects.create(
            product=self.hoodie, partner=self.partner, partner_sku="HOODIE01", 
            price=Decimal("80.00"), num_in_stock=30, num_allocated=0
        )
        
        self.user = User.objects.create_user(username="student", password="password")
        self.strategy = Strategy()
        self.country = Country.objects.create(iso_3166_1_a2='PL', name='Poland')

    def _get_basket(self):
        basket = Basket.objects.create()
        basket.strategy = self.strategy
        return basket

    def _place_order(self, basket, user):
        shipping_address = ShippingAddress(
            first_name='Jan', last_name='Kowalski',
            line1='Uliczna 1', line4='Warszawa', postcode='00-001',
            country=self.country
        )
        shipping_address.save()

        billing_address = BillingAddress(
            first_name='Jan', last_name='Kowalski',
            line1='Uliczna 1', line4='Warszawa', postcode='00-001',
            country=self.country
        )
        billing_address.save()

        shipping_method = Free()
        shipping_charge = shipping_method.calculate(basket)
        
        calculator = OrderTotalCalculator()
        total = calculator.calculate(basket, shipping_charge)

        order_creator = OrderCreator()
        order = order_creator.place_order(
            basket=basket, user=user, shipping_address=shipping_address,
            shipping_method=shipping_method, shipping_charge=shipping_charge,
            billing_address=billing_address, total=total, status='Pending'
        )
        basket.submit()
        return order

    def test_order_creation_with_single_product(self):
        basket = self._get_basket()
        basket.add_product(self.mug, quantity=2)
        order = self._place_order(basket=basket, user=self.user)
        
        self.assertIsNotNone(order.pk)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.lines.count(), 1)
        self.assertEqual(order.total_excl_tax, Decimal("30.00"))
        self.assertEqual(order.status, 'Pending')

    def test_order_creation_with_multiple_products(self):
        basket = self._get_basket()
        basket.add_product(self.mug, quantity=1)
        basket.add_product(self.hoodie, quantity=1)
        order = self._place_order(basket=basket, user=self.user)
        
        self.assertEqual(order.lines.count(), 2)
        self.assertEqual(order.total_excl_tax, Decimal("15.00") + Decimal("80.00"))
        self.assertEqual(order.num_items, 2)

    def test_placing_order_submits_basket(self):
        """
        Test that a basket's status is changed to 'Submitted' after order placement.
        """
        basket = self._get_basket()
        basket.add_product(self.hoodie)
        self.assertEqual(basket.status, Basket.OPEN)
        
        self._place_order(basket=basket, user=self.user)
        
        # With TransactionTestCase, the change is committed and a simple get() will see it.
        reloaded_basket = Basket.objects.get(pk=basket.pk)
        self.assertEqual(reloaded_basket.status, Basket.SUBMITTED)

    def test_stock_allocation_on_order_placement(self):
        self.assertEqual(self.mug_stock.num_allocated, 0)
        
        basket = self._get_basket()
        basket.add_product(self.mug, quantity=5)
        self._place_order(basket=basket, user=self.user)
        
        # We need to re-fetch the stock record as well in a transaction test case
        self.mug_stock.refresh_from_db()
        self.assertEqual(self.mug_stock.num_allocated, 5)
        self.assertEqual(self.mug_stock.net_stock_level, 45)
