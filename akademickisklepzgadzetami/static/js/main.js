const basketModal = document.querySelector('[data-basket-modal]');
const basketContent = document.querySelector('[data-basket-content]');
const basketWrapper = document.querySelector('[data-basket-wrapper]');
const basketTotal = document.querySelector('[data-basket-total]');
const basketCounter = document.querySelector('[data-basket-counter]');

let isBasketOpen = false;
// Global variable for the notification container
let notificationContainerElement;

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

    // 1. Zaktualizuj zawartość modala (zawsze)
    basketContent.innerHTML = '';

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

    // 2. Zaktualizuj globalne wskaźniki (licznik, suma)
    if (basketCounter) {
        basketCounter.innerText = data.items_count;
        basketCounter.classList.remove('hidden');
        if (data.items_count === 0) basketCounter.classList.add('hidden');
    }
    document.querySelectorAll('[data-basket-total]').forEach(el => el.innerText = `${data.total_price}`);

    // 3. Jeśli jesteśmy na stronie koszyka, odśwież jej zawartość
    const mainBasketContainer = document.getElementById('basket-content-wrapper');
    if (mainBasketContainer) {
        try {
            // Pobierz HTML strony koszyka
            const response = await fetch(window.location.href);
            const html = await response.text();

            // Użyj DOMParser do stworzenia nowego dokumentu w pamięci
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Znajdź nowy kontener w odpowiedzi
            const newMainBasketContainer = doc.getElementById('basket-content-wrapper');

            // Jeśli znaleziono, zamień starą zawartość na nową
            if (newMainBasketContainer) {
                mainBasketContainer.innerHTML = newMainBasketContainer.innerHTML;
            }
        } catch (error) {
            console.error('Błąd odświeżania widoku koszyka:', error);
            // W razie błędu można awaryjnie przeładować stronę
            // window.location.reload(); 
        }
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
    if(!productItem) {
        console.error('Nie znaleziono produktu');
        return;
    }

    const productId = productItem.dataset.id;
    const csrftoken = getCookie('csrftoken');

    console.log('Dodawanie produktu:', productId);

    try {
        // Wysyłamy POST na /api/basket/add/ z produktem
        const response = await fetch('/api/basket/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `product_id=${productId}&quantity=1`
        });

        if(response.ok) {
            console.log('Produkt dodany');
            openBasket(); // Otwórz i odśwież koszyk
        } else {
            console.error('Błąd dodawania, status:', response.status);
            // Spróbuj alternatywny URL
            console.log('Próbuję alternatywnego URL...');
        }
    } catch(err) {
        console.error('Błąd:', err);
    }
}

// Zmiana ilości (Obsługa + / - w modalu)
async function updateQuantity(lineId, newQuantity) {
    if (newQuantity < 1) {
        // Jeśli 0, usuwamy
        return deleteLine(lineId);
    }

    const csrftoken = getCookie('csrftoken');
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
        if (data.status === 'ok') {
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
async function deleteLine(lineId) {
    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch('/api/basket/update-line/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `line_id=${lineId}&quantity=0`
        });

        if (response.ok) {
            await updateBasketView();
        } else {
            const data = await response.json();
            console.error('Błąd usuwania:', data.message || response.statusText);
        }
    } catch (error) {
        console.error('Błąd sieci podczas usuwania:', error);
    }
}

// Inicjalizacja przy starcie
document.addEventListener('DOMContentLoaded', () => {
    updateBasketView();
    notificationContainerElement = document.getElementById('notification-container'); // Initialize here
});

// Function to display a notification
function displayNotification(message, type = 'info') {
    let container = notificationContainerElement; // Use the globally cached element

    // Fallback: If container is not initialized by DOMContentLoaded (e.g., very fast click)
    if (!container) {
        container = document.getElementById('notification-container');
        if (!container) {
            // If still not found, create it dynamically
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'fixed top-4 right-4 flex flex-col gap-2 z-[100]'; // Apply the same Tailwind classes
            document.body.appendChild(container);
            // Cache it for future calls
            notificationContainerElement = container; // Cache the dynamically created element
        }
    }

    if (!container) { // Should not happen after dynamic creation, but for safety
        console.warn("Notification container could not be found or created.");
        return;
    }

    let alertClasses = "bg-blue-100 text-blue-800 border-blue-400"; // Default to info
    let iconSvg = `<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>`; // Default info icon

    if (type === 'error' || type === 'danger') {
        alertClasses = "bg-red-100 text-red-800 border-red-400";
        iconSvg = `<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>`;
    } else if (type === 'success') {
        alertClasses = "bg-green-100 text-green-800 border-green-400";
        iconSvg = `<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>`;
    } else if (type === 'warning') {
        alertClasses = "bg-yellow-100 text-yellow-800 border-yellow-400";
        iconSvg = `<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.487 0L17.618 15.42c.766 1.36-.217 3.08-1.743 3.08H4.125c-1.526 0-2.509-1.72-1.743-3.08L8.257 3.099zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>`;
    }

    const notificationDiv = document.createElement('div');
    notificationDiv.className = `mb-2 p-4 rounded-lg shadow-md border-l-4 ${alertClasses} relative`;
    notificationDiv.setAttribute('role', 'alert');
    notificationDiv.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0 mr-3">
                ${iconSvg}
            </div>
            <div class="flex-grow">
                ${message}
            </div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 bg-transparent text-gray-500 rounded-lg focus:ring-2 focus:ring-gray-400 p-1.5 hover:bg-gray-200 inline-flex h-8 w-8" aria-label="Close">
                <span class="sr-only">Close</span>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
            </button>
        </div>
    `;

    // Add dismiss functionality
    notificationDiv.querySelector('button').addEventListener('click', () => {
        notificationDiv.remove();
    });

    container.appendChild(notificationDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notificationDiv.remove();
    }, 5000);
}

// Function to handle adding product to wishlist via AJAX
async function addProductToWishlist(event) {
    event.preventDefault(); // Prevent default form submission

    const form = event.target.closest('form');
    if (!form) {
        console.error("Could not find parent form for wishlist button.");
        displayNotification("Wystąpił błąd podczas dodawania do listy życzeń.", "error");
        return;
    }

    const url = form.action;
    const csrftoken = getCookie('csrftoken');
    const productId = event.target.closest('[data-product-id]').dataset.productId;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `action=add&product_pk=${productId}`
        });

        if (response.ok) { // This means status is 2xx after all redirects
            displayNotification("Produkt został dodany do listy życzeń!", "success");
            // Removed client-side redirect: window.location.href = "http://127.0.0.1:8000/shop/accounts/wishlists/";
        } else {
            const errorText = await response.text();
            console.error('Błąd dodawania do listy życzeń:', response.status, errorText);
            displayNotification("Wystąpił błąd podczas dodawania do listy życzeń.", "error");
        }
    } catch (error) {
        console.error('Błąd sieci podczas dodawania do listy życzeń:', error);
        displayNotification("Wystąpił błąd sieci podczas dodawania do listy życzeń.", "error");
    }
}

// Handler dla formularza dodawania do koszyka na stronie szczegółów produktu
const addToBasketForm = document.getElementById('add_to_basket_form');
if (addToBasketForm) {
    addToBasketForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const csrftoken = getCookie('csrftoken');
        const formData = new FormData(addToBasketForm);
        
        try {
            const response = await fetch(addToBasketForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            if (response.ok) {
                displayNotification('Produkt dodany do koszyka!', 'success');
                await updateBasketView();
                openBasket();
            } else {
                displayNotification('Błąd dodawania produktu do koszyka', 'error');
            }
        } catch (error) {
            console.error('Błąd:', error);
            displayNotification('Błąd sieci przy dodawaniu do koszyka', 'error');
        }
    });
}
// Wishlist Modal Functions
let currentProductId = null;

function handleWishlistClick(event, productId) {
    event.preventDefault();
    event.stopPropagation(); // Zabezpieczenie - zapobiega propagacji kliknięcia do parentów
    
    // Sprawdzenie czy modal istnieje na stronie (czyli czy jesteśmy na stronie z base.html)
    const modal = document.getElementById('wishlist-modal');
    if (!modal) {
        // Jeśli modalu nie ma (np. na home.html), przekieruj do logowania
        displayNotification("Aby dodać do listy życzeń, musisz się zalogować.", "info");
        window.location.href = '/shop/accounts/login/';
        return;
    }
    
    openWishlistModal(event, productId);
}

function openWishlistModal(event, productId) {
    event.preventDefault();
    
    // Sprawdzenie czy modal istnieje na stronie
    const modal = document.getElementById('wishlist-modal');
    if (!modal) {
        displayNotification("Modal listy życzeń nie jest dostępny. Przejdź do strony z logowaniem.", "error");
        return;
    }
    
    currentProductId = productId;
    modal.style.display = 'flex';
    
    // Pobierz wishlists zaraz po otwarciu modalu
    loadWishlists();
}

async function loadWishlists() {
    try {
        const response = await fetch('/api/wishlists/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        
        if (!response.ok) {
            console.error('Response not ok:', response.status, response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
      
        const modalContent = document.getElementById('wishlist-modal-content');
        
        // Jeśli jest błąd w odpowiedzi
        if (data.error) {
            console.error('API Error:', data.error);
            modalContent.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-red-600">Błąd: ${data.error}</p>
                    <p class="text-red-400 text-sm mt-2">Authenticated: ${data.authenticated}</p>
                </div>
            `;
            return;
        }
        
        if (data.wishlists && data.wishlists.length > 0) {
            modalContent.innerHTML = data.wishlists.map(wishlist => `
                <button 
                    type="button" 
                    onclick="selectWishlist(${wishlist.id}, event)" 
                    class="w-full p-4 text-left bg-gray-50 hover:bg-[#015F8A] hover:text-white rounded-lg transition-all border border-gray-200 hover:border-[#015F8A]"
                >
                    <div class="font-medium">${wishlist.name}</div>
                </button>
            `).join('');
        } else {
            modalContent.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600">Nie masz jeszcze żadnych list życzeń.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading wishlists:', error);
        const modalContent = document.getElementById('wishlist-modal-content');
        modalContent.innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600">Błąd przy ładowaniu list życzeń.</p>
                <p class="text-red-400 text-sm mt-2">${error.message}</p>
            </div>
        `;
    }
}

function closeWishlistModal() {
    const modal = document.getElementById('wishlist-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    const input = document.getElementById('new-wishlist-name');
    if (input) {
        input.value = '';
    }
    currentProductId = null;
}

function selectWishlist(wishlistId, event) {
    event.preventDefault();
    addProductToWishlistId(currentProductId, wishlistId);
}

async function addProductToWishlistId(productId, wishlistId) {
    const csrftoken = getCookie('csrftoken');
    
    try {
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('wishlist_id', wishlistId);
        
        const response = await fetch('/api/wishlist/add-product/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

        const data = await response.json();
      
        if (response.ok && data.status === 'success') {
            displayNotification("Produkt został dodany do listy życzeń!", "success");
            closeWishlistModal();
        } else {
            displayNotification(`Błąd: ${data.message || 'Nie udało się dodać produktu'}`, "error");
        }
    } catch (error) {
        console.error('Error:', error);
        displayNotification(`Błąd sieci: ${error.message}`, "error");
    }
}

async function createAndAddWishlist(event) {
    event.preventDefault();
    const wishlistName = document.getElementById('new-wishlist-name').value.trim();
    
    if (!wishlistName) {
        displayNotification("Proszę wpisać nazwę listy życzeń.", "error");
        return;
    }

    const csrftoken = getCookie('csrftoken');
    
    try {
        // Tworzymy nową listę
        const createResponse = await fetch('/shop/accounts/wishlists/create/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `name=${encodeURIComponent(wishlistName)}`
        });

        if (createResponse.ok) {
            // Odczytujemy ID nowej listy z odpowiedzi
            const data = await createResponse.json();
            const wishlistId = data.id || data.key;
            
            // Dodajemy produkt do nowej listy
            await addProductToWishlistId(currentProductId, wishlistId);
        } else {
            displayNotification("Błąd przy tworzeniu listy życzeń.", "error");
        }
    } catch (error) {
        console.error('Error:', error);
        displayNotification("Błąd sieci.", "error");
    }
}

// Zamknij modal gdy kliknięto poza nim
document.addEventListener('click', function(event) {
    const modal = document.getElementById('wishlist-modal');
    if (modal && event.target === modal) {
        closeWishlistModal();
    }
});