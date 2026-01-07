const basketModal = document.querySelector('[data-basket-modal]');
const basketContent = document.querySelector('[data-basket-content]');
const basketWrapper = document.querySelector('[data-basket-wrapper]');
const basketTotal = document.querySelector('[data-basket-total]');
const basketCounter = document.querySelector('[data-basket-counter]');

let isBasketOpen = false;

// Pobieramy CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funkcja pobierająca stan koszyka z serwera
async function fetchBasketData() {
    try {
        const response = await fetch('/shop/basket/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        if (!response.ok) throw new Error('Błąd sieci');
        return await response.json();
    } catch (error) {
        console.error('Błąd pobierania koszyka:', error);
        return null;
    }
}

// Renderowanie koszyka na podstawie danych z serwera
async function updateBasketView() {
    const data = await fetchBasketData();
    if (!data) return;

    basketContent.innerHTML = '';

    // Aktualizacja licznika na navbarze
    if (basketCounter) {
        basketCounter.innerText = data.items_count;
        basketCounter.classList.remove('hidden');
        if (data.items_count === 0) basketCounter.classList.add('hidden');
    }

    // Aktualizacja sumy
    if (basketTotal) basketTotal.innerText = `${data.total_price}`;

    if (data.products.length === 0) {
        basketContent.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-gray-500 opacity-60">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                <p>Twój koszyk jest pusty</p>
            </div>
        `;
    } else {
        data.products.forEach(product => {
            basketContent.innerHTML += createProductHTML(product);
        });
    }
}

// HTML dla pojedynczego produktu w koszyku
function createProductHTML(product) {
    return `
        <div class="bg-gray-50 p-3 rounded-2xl flex gap-4 relative group border border-gray-100 hover:border-blue-200 transition-colors">
            <div class="w-20 h-20 bg-white rounded-xl p-2 shadow-sm border border-gray-100 flex-shrink-0" style="width: 8rem; height: 8rem;">
                <img src="${product.image || '/static/theme/images/placeholder.png'}" class="w-full h-full object-contain" style="width: 100%; height: 100%; object-fit: contain;">
            </div>
            
            <div class="flex-1 min-w-0 flex flex-col justify-center">
                <h4 class="text-gray-900 font-bold text-sm leading-tight mb-1 pr-6">
                    <a href="#" class="hover:text-blue-600 transition-colors">${product.name}</a>
                </h4>
                <p class="text-gray-400 text-xs mb-3">Cena jedn.: ${product.price}</p>
                
                <div class="flex items-center justify-between mt-2">
                    <div class="flex items-center bg-white rounded-lg border border-gray-200 shadow-sm">
                        <button onclick="updateQuantity(${product.line_id}, ${product.quantity - 1})" class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-[#015F8A] hover:bg-blue-50 rounded-l-lg transition-colors">
                            -
                        </button>
                        <span class="text-gray-900 text-sm font-bold w-8 text-center">${product.quantity}</span>
                        <button onclick="updateQuantity(${product.line_id}, ${product.quantity + 1})" class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-[#015F8A] hover:bg-blue-50 rounded-r-lg transition-colors">
                            +
                        </button>
                    </div>
                    
                    <span class="text-[#015F8A] font-bold text-sm bg-blue-50 px-2 py-1 rounded-md">
                        ${product.total}
                    </span>
                </div>
            </div>

            <button onclick="deleteLine(${product.line_id})" class="absolute top-2 right-2 text-gray-300 hover:text-red-500 hover:bg-red-50 p-1.5 rounded-lg transition-all" title="Usuń">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
            </button>
        </div>
    `;
}

// Logika otwierania/zamykania
function openBasket(){
    isBasketOpen = true;
    basketModal.classList.remove('translate-x-full', 'translate-x-0');
    basketModal.classList.add('translate-x-0');

    basketWrapper.classList.remove('pointer-events-none', 'bg-transparent');
    basketWrapper.classList.add('pointer-events-auto', 'bg-black/50', 'backdrop-blur-sm');

    updateBasketView(); // Pobierz świeże dane
}

function closeBasket(){
    isBasketOpen = false;
    basketModal.classList.remove('translate-x-0');
    basketModal.classList.add('translate-x-full');

    basketWrapper.classList.remove('pointer-events-auto', 'bg-black/50', 'backdrop-blur-sm');
    basketWrapper.classList.add('pointer-events-none', 'bg-transparent');
}

basketWrapper.addEventListener('click', (e) => {
    if(e.target === basketWrapper) closeBasket();
});

// Dodawanie produktu (z listy produktów)
async function addProductToBasket(e){
    // Pobieramy dane z atrybutów HTML elementu rodzica
    const productItem = e.target.closest('[data-product-item]');
    if(!productItem) return;

    const productId = productItem.dataset.id;
    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch(`/shop/basket/add/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest' // Ważne dla naszego widoku
            },
            body: 'quantity=1'
        });

        if(response.ok) {
            openBasket(); // Otwórz i odśwież koszyk
        } else {
            console.error('Błąd dodawania');
        }
    } catch(err) {
        console.error(err);
    }
}

// Zmiana ilości (Obsługa + / - w modalu)
// UWAGA: Oscar nie ma domyślnego endpointu JSON do zmiany ilości jednej linii w prosty sposób
// Musimy wysłać formularz POST na /shop/basket/
// Dla uproszczenia w tym projekcie, założymy że formularz koszyka jest standardowy
// i użyjemy sztuczki z przesyłaniem formularza formsetu, ale to skomplikowane w czystym AJAX.
// Lepsze podejście: usuń linię i dodaj produkt ponownie (dla +) lub zmniejsz.
// Ale Oscar obsługuje update linii via POST. Zróbmy to tak:

async function updateQuantity(lineId, newQuantity) {
    if (newQuantity < 1) {
        // Jeśli 0, usuwamy (zakładam, że deleteLine masz już zrobione)
        return deleteLine(lineId);
    }

    // Pobieramy token CSRF (wymagany przez Django przy POST)
    const csrftoken = getCookie('csrftoken');

    // Budujemy dane formularza
    const formData = new FormData();
    formData.append('line_id', lineId);
    formData.append('quantity', newQuantity);

    try {
        const response = await fetch('/api/basket/update-line/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        });

        const data = await response.json();
        console.log(data)
        if (data.status === 'ok') {
            // Odświeżamy cały widok koszyka, aby zaktualizować licznik, sumę i listy
            await updateBasketView();
        } else {
            console.error('Błąd aktualizacji:', data.message);
            alert('Wystąpił błąd podczas aktualizacji koszyka.');
        }

    } catch (error) {
        console.error('Błąd sieci:', error);
    }
}

// Usuwanie linii z koszyka
// Usuwanie linii z koszyka
async function deleteLine(lineId) {
    const csrftoken = getCookie('csrftoken');

    try {
        // Używamy tego samego endpointu API co przy zmianie ilości.
        // W views.py zaimplementowaliśmy logikę: jeśli quantity <= 0 -> line.delete()
        // Upewnij się, że URL '/api/basket/update-line/' odpowiada temu zdefiniowanemu w urls.py
        const response = await fetch('/api/basket/update-line/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            // Przesyłamy quantity=0, aby wymusić usunięcie
            body: `line_id=${lineId}&quantity=0`
        });

        if (response.ok) {
            // Jeśli sukces, odświeżamy widok koszyka (AJAX) bez przeładowania strony
            await updateBasketView();
        } else {
            const data = await response.json();
            console.error('Błąd usuwania:', data.message || response.statusText);
        }
    } catch (error) {
        console.error('Błąd sieci podczas usuwania:', error);
    }
}

// Inicjalizacja przy starcie (żeby licznik był ok)
document.addEventListener('DOMContentLoaded', () => {
    updateBasketView();
});