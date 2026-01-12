from decimal import Decimal
from django.test import TestCase
from oscar.core.loading import get_model

# Correctly load all necessary models
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')

class UniversityPartnerModelsTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(name="University Stationery")
        self.pen = Product.objects.create(title="University Pen", product_class=self.product_class)
        self.notebook = Product.objects.create(title="University Notebook", product_class=self.product_class)
        
        self.campus_store = Partner.objects.create(name="Campus Bookstore")
        self.online_warehouse = Partner.objects.create(name="Online Warehouse")

    def test_partner_creation(self):
        self.assertEqual(self.campus_store.name, "Campus Bookstore")
        self.assertIsNotNone(self.campus_store.code)

    def test_stockrecord_creation_for_pen(self):
        stockrecord = StockRecord.objects.create(
            product=self.pen,
            partner=self.campus_store,
            partner_sku="U-PEN-01",
            price=Decimal("5.00"),
            num_in_stock=200
        )
        self.assertEqual(stockrecord.product, self.pen)
        self.assertEqual(stockrecord.partner, self.campus_store)
        self.assertEqual(stockrecord.num_in_stock, 200)
        self.assertEqual(stockrecord.price, Decimal("5.00"))

    def test_multiple_partners_for_one_product(self):
        StockRecord.objects.create(
            product=self.notebook, partner=self.campus_store, partner_sku='NB-CS-01',
            price=Decimal("12.00"), num_in_stock=50
        )
        StockRecord.objects.create(
            product=self.notebook, partner=self.online_warehouse, partner_sku='NB-OW-01',
            price=Decimal("11.50"), num_in_stock=150
        )
        self.assertEqual(self.notebook.stockrecords.count(), 2)
        self.assertTrue(self.notebook.has_stockrecords)

    def test_stock_allocation_and_consumption(self):
        stockrecord = StockRecord.objects.create(
            product=self.pen, partner=self.campus_store, partner_sku="U-PEN-02", 
            price=Decimal("5.00"), num_in_stock=50
        )
        
        stockrecord.allocate(10)
        self.assertEqual(stockrecord.num_allocated, 10)
        self.assertEqual(stockrecord.net_stock_level, 40)
        
        stockrecord.consume_allocation(7)
        self.assertEqual(stockrecord.num_allocated, 3)
        self.assertEqual(stockrecord.num_in_stock, 43)
        self.assertEqual(stockrecord.net_stock_level, 40)

    def test_cancel_stock_allocation(self):
        stockrecord = StockRecord.objects.create(
            product=self.notebook, partner=self.online_warehouse, partner_sku="U-NOTE-01",
            price=Decimal("12.00"), num_in_stock=30
        )
        stockrecord.allocate(15)
        self.assertEqual(stockrecord.num_allocated, 15)
        
        stockrecord.cancel_allocation(5)
        self.assertEqual(stockrecord.num_allocated, 10)
        self.assertEqual(stockrecord.net_stock_level, 20)

    def test_product_is_unavailable_without_stockrecord(self):
        unstocked_product = Product.objects.create(title="Stapler", product_class=self.product_class)
        self.assertFalse(unstocked_product.has_stockrecords)
