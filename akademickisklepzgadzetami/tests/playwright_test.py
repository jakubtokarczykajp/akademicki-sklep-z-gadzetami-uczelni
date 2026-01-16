import pytest
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model
from decimal import Decimal
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def create_test_data(db):
    """Tworzy dane testowe: produkt, partner, stock, użytkownika, kraj"""
    Product = get_model('catalogue', 'Product')
    ProductClass = get_model('catalogue', 'ProductClass')
    Partner = get_model('partner', 'Partner')
    StockRecord = get_model('partner', 'StockRecord')
    Country = get_model('address', 'Country')
    User = get_user_model()

    country = Country.objects.create(
        iso_3166_1_a2='PL',
        name='Poland'
    )

    product_class = ProductClass.objects.create(
        name="University Gadgets",
        requires_shipping=True
    )

    product = Product.objects.create(
        title="Akcesoria - zestaw nr 1 (jesień)",
        product_class=product_class,
        is_public=True
    )

    partner = Partner.objects.create(name="Sklep Uczelniany")

    stock_record = StockRecord.objects.create(
        product=product,
        partner=partner,
        price=Decimal("60.00"),
        num_in_stock=50
    )

    user = User.objects.create_user(
        username='student_playwright',
        password='testpassword'
    )

    return {
        "product": product,
        "user": user,
        "stock_record": stock_record,
        "country": country,
    }


import pytest
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model
from decimal import Decimal
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def create_test_data(db):
    """Tworzy dane testowe: produkt, partner, stock, użytkownika, kraj"""
    Product = get_model('catalogue', 'Product')
    ProductClass = get_model('catalogue', 'ProductClass')
    Partner = get_model('partner', 'Partner')
    StockRecord = get_model('partner', 'StockRecord')
    Country = get_model('address', 'Country')
    User = get_user_model()

    country = Country.objects.create(
        iso_3166_1_a2='PL',
        name='Poland'
    )

    product_class = ProductClass.objects.create(
        name="University Gadgets",
        requires_shipping=True
    )

    product = Product.objects.create(
        title="Akcesoria - zestaw nr 1 (jesień)",
        product_class=product_class,
        is_public=True
    )

    partner = Partner.objects.create(name="Sklep Uczelniany")

    stock_record = StockRecord.objects.create(
        product=product,
        partner=partner,
        price=Decimal("60.00"),
        num_in_stock=50
    )

    user = User.objects.create_user(
        username='student_playwright',
        password='testpassword'
    )

    return {
        "product": product,
        "user": user,
        "stock_record": stock_record,
        "country": country,
    }


@pytest.mark.django_db
def test_full_checkout_flow_as_new_user_playwright(page: Page, live_server, create_test_data):
    """Test pełnego procesu checkout dla nowo zarejestrowanego użytkownika w Django Oscar"""
    Order = get_model('order', 'Order')
    product = create_test_data["product"]
    stock_record = create_test_data["stock_record"]

    # 1. Wejdź na stronę logowania/rejestracji z redirectem
    register_url = f"{live_server.url}/shop/accounts/login/?next=/shop/checkout/"
    page.goto(register_url)

    # Formularz rejestracji to drugi formularz na stronie
    register_form = page.locator("form[action='/shop/accounts/login/']").nth(1)

    # Wypełnij formularz rejestracji
    email_input = page.locator("input[name='registration-email']")
    password1_input = page.locator("input[name='registration-password1']")
    password2_input = page.locator("input[name='registration-password2']")

    # Wygeneruj losowego użytkownika, żeby nie kolidować z DB
    import random
    random_email = f"user{random.randint(1000,9999)}@example.com"
    password = "TestPassword123!"

    email_input.fill(random_email)
    email_input.dispatch_event("input")

    password1_input.fill(password)
    password1_input.dispatch_event("input")

    password2_input.fill(password)
    password2_input.dispatch_event("input")

    # Submit formularza rejestracji
    register_form.locator("button[type='submit']").click()

    product = create_test_data["product"]
    product_url = live_server.url + product.get_absolute_url()
    page.goto(product_url)
    # 2. Dodaj produkt do koszyka
    add_to_basket_button = page.get_by_role("button", name="Dodaj do koszyka")
    add_to_basket_button.click()

    # 3. Przejdź do koszyka
    page.goto(f"{live_server.url}/shop/basket/")
    page.goto(f"{live_server.url}/shop/checkout/")

    # id formularza: new_shipping_address
    shipping_form = page.locator("#new_shipping_address")

    # Wypełnienie pól wymaganych
    shipping_form.locator("#id_first_name").fill("Jan")
    shipping_form.locator("#id_last_name").fill("Kowalski")
    shipping_form.locator("#id_line1").fill("ul. Przykładowa 1")
    shipping_form.locator("#id_line4").fill("Gorzów Wielkopolski")
    shipping_form.locator("#id_postcode").fill("66-400")
    country_select = shipping_form.locator("#id_country")

    page.evaluate("""
                  const select = document.querySelector('#id_country');
                  select.value = 'PL';
                  select.dispatchEvent(new Event('change', {bubbles: true}));
                  """)

    # Opcjonalne pola
    shipping_form.locator("#id_line2").fill("Mieszkanie 2")
    shipping_form.locator("#id_line3").fill("Blok 5")
    shipping_form.locator("#id_state").fill("Lubuskie")
    shipping_form.locator("#id_phone_number").fill("+48 600 700 800")
    shipping_form.locator("#id_notes").fill("Proszę o szybką wysyłkę")

    # Kliknięcie przycisku 'Dalej'
    shipping_form.locator("button[type='submit']").click()

    # 3. Payment (dummy)
    expect(page).to_have_url(live_server.url + "/checkout/payment-details/")
    page.get_by_role("button", name="Continue").click()

    # 4. Preview
    expect(page).to_have_url(live_server.url + "/checkout/preview/")
    page.get_by_role("button", name="Place order").click()

    # 5. Thank you page
    expect(page).to_have_url(live_server.url + "/checkout/thank-you/")
    header = page.locator("h1")
    expect(header).to_have_text("Confirmation")

    # 6. Validate order in DB
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(email=random_email)

    assert Order.objects.count() == 1
    order = Order.objects.first()
    assert order.user == user
    assert order.total_incl_tax == stock_record.price
    assert order.status == "Pending"