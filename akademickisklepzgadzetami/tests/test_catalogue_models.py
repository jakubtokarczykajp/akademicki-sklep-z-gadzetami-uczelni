from decimal import Decimal
from django.test import TestCase
from django.utils.text import slugify
from oscar.core.loading import get_model, get_class

# Use get_model and get_class for robust dynamic loading
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Strategy = get_class('partner.strategy', 'Default')

class UniversityCatalogueModelsTest(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(
            name="University Gadgets", slug="university-gadgets", track_stock=True
        )
        self.apparel_category = Category.add_root(name="Apparel")
        self.partner = Partner.objects.create(name="University Store")
        self.strategy = Strategy()

    def test_product_creation_mug(self):
        product = Product.objects.create(
            title="University Mug", product_class=self.product_class
        )
        self.assertEqual(product.slug, slugify("University Mug"))
        self.assertEqual(product.title, "University Mug")

    def test_product_with_category_hoodie(self):
        product = Product.objects.create(
            title="University Hoodie", product_class=self.product_class
        )
        product.categories.add(self.apparel_category)
        self.assertEqual(product.categories.count(), 1)
        self.assertEqual(product.categories.first(), self.apparel_category)

    def test_category_tree_for_apparel(self):
        parent = Category.add_root(name="Clothing", slug="clothing")
        child = parent.add_child(name="Hoodies", slug="hoodies")
        self.assertEqual(child.get_parent(), parent)
        self.assertEqual(child.depth, 2)
        self.assertEqual(str(child), "Clothing > Hoodies")

    def test_product_is_purchasable_with_stockrecord(self):
        """
        Test that a product is purchasable only when it has a stock record.
        """
        product = Product.objects.create(
            title="University Pen", product_class=self.product_class
        )
        
        # Use the strategy to fetch purchase info
        info = self.strategy.fetch_for_product(product)
        self.assertFalse(info.availability.is_available_to_buy)

        # Now create a stock record
        StockRecord.objects.create(
            product=product,
            partner=self.partner,
            partner_sku='PEN-01',
            price=Decimal("4.99"),
            num_in_stock=100
        )

        # Fetch info again
        info = self.strategy.fetch_for_product(product)
        self.assertTrue(info.availability.is_available_to_buy)
        self.assertEqual(info.price.excl_tax, Decimal("4.99"))
