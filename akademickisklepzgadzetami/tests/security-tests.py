from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
User = get_user_model()

class SecurityAndSessionTest(TestCase):

    def setUp(self):
        self.password = "plain_text_password"
        self.user = User.objects.create_user(username="testuser", password=self.password)
        product_class = ProductClass.objects.create(
            name="Books", requires_shipping=True
        )
        self.product = Product.objects.create(
            title="Test Book", product_class=product_class, is_public=True
        )
        partner = Partner.objects.create(name="Book Supplier")
        StockRecord.objects.create(
            product=self.product, partner=partner, price=10.00, num_in_stock=10
        )

    def test_password_is_hashed_in_database(self):
        user_from_db = User.objects.get(username="testuser")
        self.assertNotEqual(user_from_db.password, self.password)
        self.assertTrue(user_from_db.check_password(self.password))

    def test_csrf_protection_forbids_post_request(self):
        login_url = reverse('customer:login')
        response = self.client.post(
            login_url, {"username": "testuser", "password": "password"}, enforce_csrf_checks=True
        )
        self.assertEqual(response.status_code, 400)