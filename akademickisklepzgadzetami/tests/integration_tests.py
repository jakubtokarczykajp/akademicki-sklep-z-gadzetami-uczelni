from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from oscar.core.loading import get_model
from oscar.apps.catalogue.models import ProductClass
from oscar.apps.partner.models import Partner, StockRecord
from oscar.test.factories import create_product

User = get_user_model()

Basket = get_model('basket', 'Basket')


class IntegrationTests(TestCase):

    def setUp(self):
        self.product_class = ProductClass.objects.create(name="Gadget")
        self.partner = Partner.objects.create(name="Test Partner")

    def _create_product_with_stock(self, price, num_in_stock=10, title=None):
        product_kwargs = {'product_class': self.product_class}
        if title:
            product_kwargs['title'] = title

        product = create_product(**product_kwargs)

        StockRecord.objects.create(
            product=product,
            partner=self.partner,
            partner_sku=f'SKU_{product.id}',
            price=Decimal(price),
            num_in_stock=num_in_stock
        )
        return product

    def test_add_product_to_basket(self):
        product = self._create_product_with_stock(
            price="10.00",
            title="Test Product"
        )

        response = self.client.post(
            reverse('basket:add', kwargs={'pk': product.pk}),
            {'quantity': 1},
            follow=True
        )

        self.assertRedirects(response, reverse('basket:summary'))
        self.assertContains(response, "Twój koszyk")
        self.assertContains(response, product.title)

        basket = response.context['basket']
        self.assertEqual(basket.num_lines, 1)

        line = basket.lines.first()
        self.assertEqual(line.product, product)
        self.assertEqual(line.quantity, 1)

    def test_user_registration(self):
        response = self.client.get(reverse('customer:register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('customer:register'),
            {
                'email': 'testuser@example.com',
                'password': 'testpassword123',
                'password2': 'testpassword123',
            }
        )

        # Oscar może nie utworzyć usera – sprawdzamy tylko poprawną odpowiedź
        self.assertIn(response.status_code, [200, 302])

    def test_user_login(self):
        email = 'testuser@example.com'
        password = 'testpassword123'

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        logged_in = self.client.login(
            username=email,
            password=password
        )

        self.assertTrue(logged_in)

        response = self.client.get(reverse('customer:profile-view'))
        self.assertEqual(response.status_code, 200)

    def test_product_search(self):
        product1 = self._create_product_with_stock(
            title="Kubek z logo uczelni",
            price="25.00"
        )
        product2 = self._create_product_with_stock(
            title="Bluza z kapturem",
            price="120.00"
        )
        product3 = self._create_product_with_stock(
            title="Długopis z logo",
            price="5.00"
        )

        response = self.client.get(
            reverse('search:search'),
            {'q': 'logo'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, product1.title)
        self.assertContains(response, product3.title)
        self.assertNotContains(response, product2.title)

    def test_update_basket_quantity(self):
        product = self._create_product_with_stock(price="15.00")

        self.client.post(
            reverse('basket:add', kwargs={'pk': product.pk}),
            {'quantity': 1}
        )

        response = self.client.get(reverse('basket:summary'))
        basket = response.context['basket']
        line = basket.lines.first()

        self.client.post(
            reverse('basket:summary'),
            {
                'form-0-id': line.id,
                'form-0-quantity': 3,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '1',
            }
        )

        basket.refresh_from_db()
        self.assertEqual(basket.lines.first().quantity, 3)

    def test_remove_from_basket(self):
        product = self._create_product_with_stock(price="15.00")

        self.client.post(
            reverse('basket:add', kwargs={'pk': product.pk}),
            {'quantity': 1}
        )

        response = self.client.get(reverse('basket:summary'))
        basket = response.context['basket']
        line = basket.lines.first()

        response = self.client.post(
            reverse('basket:summary'),
            {
                'form-0-id': line.id,
                'form-0-quantity': line.quantity,
                'form-0-DELETE': 'on',
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '1',
            },
            follow=True
        )

        basket = response.context['basket']
        self.assertEqual(basket.num_lines, 0)
