from django.test import TestCase
from django.utils.text import slugify

from oscar.apps.catalogue.models import Product, ProductClass, Category
from oscar.apps.partner.models import Partner, StockRecord


class ProductModelTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(
            name="Books",
            slug="books",
            track_stock=True
        )

    def test_product_creation(self):
        product = Product.objects.create(
            title="Clean Code",
            slug=slugify("Clean Code"),
            product_class=self.product_class
        )

        self.assertEqual(product.title, "Clean Code")
        self.assertEqual(product.product_class, self.product_class)
        self.assertTrue(product.is_public)
        self.assertTrue(product.is_standalone)


class ProductModelTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(
            name="Books",
            slug="books",
            track_stock=True
        )

    def test_product_creation(self):
        product = Product.objects.create(
            title="Clean Code",
            slug=slugify("Clean Code"),
            product_class=self.product_class
        )

        self.assertEqual(product.title, "Clean Code")
        self.assertEqual(product.product_class, self.product_class)
        self.assertTrue(product.is_public)
        self.assertTrue(product.is_standalone)


class CategoryModelTest(TestCase):

    def test_category_creation(self):
        category = Category.add_root(
            name="Electronics",
            slug="electronics"
        )

        self.assertEqual(category.name, "Electronics")
        self.assertEqual(category.depth, 1)

    def test_category_tree(self):
        parent = Category.add_root(
            name="Electronics",
            slug="electronics"
        )

        child = parent.add_child(
            name="Laptops",
            slug="laptops"
        )

        self.assertEqual(child.get_parent(), parent)
        self.assertEqual(child.depth, 2)

class PartnerModelTest(TestCase):

    def test_partner_creation(self):
        partner = Partner.objects.create(
            name="Main partner"
        )

        self.assertEqual(partner.name, "Main partner")


class StockRecordModelTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(
            name="Books",
            slug="books",
            track_stock=True
        )

        self.product = Product.objects.create(
            title="DDD",
            slug="ddd",
            product_class=self.product_class
        )

        self.partner = Partner.objects.create(
            name="Warehouse"
        )

    def test_stockrecord_creation(self):
        stockrecord = StockRecord.objects.create(
            product=self.product,
            partner=self.partner,
            partner_sku="DDD-001",
            price=120,
            num_in_stock=5
        )

        self.assertEqual(stockrecord.product, self.product)
        self.assertEqual(stockrecord.partner, self.partner)
        self.assertEqual(stockrecord.num_in_stock, 5)
        self.assertGreater(stockrecord.num_in_stock, 0)