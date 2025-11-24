const basketModal = document.querySelector('[data-basket-modal]');
const basketContent = document.querySelector('[data-basket-content]');
const basketWrapper = document.querySelector('[data-basket-wrapper]');
const summaryButton = document.querySelector('[data-summary-button]');
const basketCounter = document.querySelector('[data-basket-counter]');

let isBasketOpen = false;

let localBasketState = localStorage.getItem('basket');

let products = localBasketState ? JSON.parse(localBasketState) : [];

let summaryPrice = 145;

let quantity = 2;

basketWrapper.addEventListener('click', (e) => {
    if(e.target === basketWrapper){
        closeBasket();
    }
})

function updateBasketView() {
    basketContent.innerHTML = '';
    localStorage.setItem('basket', JSON.stringify(products));
    if (products.length === 0) {
        basketContent.innerHTML = `
            <p class="text-gray-400 text-center mt-10">
                🛒 Brak przedmiotów w koszyku
            </p>
        `;

        quantity = 0;
        summaryPrice = 0;

        basketCounter.classList.remove('flex')
        basketCounter.classList.add('hidden');

         summaryButton.innerHTML = `Przejdź do podsumowania </br> 
         <span class="font-medium">${summaryPrice} zł<span/>`;
    }
    else{
        quantity = products.reduce((acc, prod) => acc + prod.quantity, 0);
        summaryPrice = products.reduce((acc, prod) => acc + prod.cost, 0);
      
        if(quantity > 0){
            basketCounter.classList.remove('hidden');
            basketCounter.classList.add('flex')
        }
        else{
            basketCounter.classList.remove('flex')
            basketCounter.classList.add('hidden');
        }

        summaryButton.innerHTML = `Przejdź do podsumowania </br> 
        <span class="font-medium">${summaryPrice} zł<span/>`;

        basketCounter.innerHTML = `${quantity}`;

        products.forEach(product => {
            basketContent.innerHTML += createProduct(product);
        })
    } 
}

function openBasket(){
    isBasketOpen = !isBasketOpen;
    if (isBasketOpen) {
        basketModal.classList.remove('translate-x-full');
        basketModal.classList.add('translate-x-0');
        basketWrapper.classList.remove('pointer-events-none', 'bg-transparent');
        basketWrapper.classList.add('pointer-events-auto', 'bg-black/50');
    } else {
        removeClassesOnClose();
    }
    updateBasketView();
}

function closeBasket(){
    isBasketOpen = false;
    removeClassesOnClose();
}

function removeClassesOnClose(){
    basketModal.classList.remove('translate-x-0');
    basketModal.classList.add('translate-x-full');
    basketWrapper.classList.remove('pointer-events-auto', 'bg-black/50');
    basketWrapper.classList.add('pointer-events-none', 'bg-transparent');
}

function addProductToBasket(e){
    const productItem = e.target.closest('[data-product-item]');

    if(!productItem) return;

    const productId = parseInt(productItem.dataset.id);

    if(products.find(product => product.id === parseInt(productItem.dataset.id))){
        increaseProductQuantity(productId);
    }
    else{
        const product = {
            name: productItem.dataset.name,
            price: parseInt(productItem.dataset.price),
            id: parseInt(productItem.dataset.id),
            image: productItem.dataset.image,
            quantity: 1,
            cost: productItem.dataset.promotion ?  
                parseInt(productItem.dataset.price) - parseInt(productItem.dataset.discount) : 
                parseInt(productItem.dataset.price),
            promotion: productItem.dataset.promotion,
            discount: parseInt(productItem.dataset.discount)
        }
        products.push(product);
    }

    updateBasketView();
    if(!isBasketOpen) openBasket();
}

function removeProductFromBasket(productId){
    products = products.filter(product => product.id !== productId);
    updateBasketView();
}

function decreaseProductQuantity(productId){
    const product = products.find(product => product.id === productId);

    if(product.quantity > 1){
         const newProduct = {
            ...product, 
            quantity: product.quantity - 1, 
            cost: product.promotion ?
            (product.price - product.discount) * (product.quantity - 1) :
            product.price * (product.quantity - 1)
        }

        const index = products.findIndex(product => product.id === productId);

        products.splice(index, 1, newProduct);

        updateBasketView();
    }
}

function increaseProductQuantity(productId){
    const product = products.find(product => product.id === productId);

    const newProduct = {
        ...product, 
        quantity: product.quantity + 1, 
        cost: 
           product.promotion ? 
           (product.price - product.discount) * (product.quantity + 1) : 
           product.price * (product.quantity + 1),
    }

    const index = products.findIndex(product => product.id === productId);

    products.splice(index, 1, newProduct);

    updateBasketView();
}

function createProduct(product){
    return `
                <div 
                    class="flex flex-col mb-2 bg-gray-600 text-white
                    p-2 rounded-md gap-2 relative"
                >
                    <div class="flex gap-2 items-end">
                        <div>
                        <img class="w-[60px] h-[70px]" src="/static/${product.image}"/>
                        </div>
                        <div class="flex flex-col h-full gap-2">
                            <div>
                                <p class="text-xs">Cena jednostkowa</p>
                                <div class="flex gap-1">
                                     <p class="text-sm font-medium">
                                    ${
                                        product.promotion ? 
                                        parseInt(product.price) - parseInt(product.discount) : 
                                        product.price} zł
                                    </p>
                                    ${
                                        product.promotion ? 
                                        `<p class="text-sm font-medium text-red-400 line-through">${product.price} zł</p>`: 
                                        ''
                                    }
                                </div>
                            </div>
                            <p 
                                class="font-semibold bg-blue-100 px-4 py-1 rounded-full
                                text-black text-sm"
                            >
                                ${product.name}
                            </p>
                        </div>
                    </div>
                    <div class="flex items-center justify-between w-full">
                       <div>
                            <p class="text-xs">Cena całkowita</p>
                            <p class="text-sm font-medium">
                                ${product.cost} zł
                            </p>
                        </div>
                        <div>
                            <div class="flex gap-1 border px-2 py-1 rounded-full">
                                <button
                                    onclick="decreaseProductQuantity(${product.id})"
                                >
                                    <svg 
                                        xmlns="http://www.w3.org/2000/svg" 
                                        width="16" height="16" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="2" 
                                        stroke-linecap="round" stroke-linejoin="round" 
                                        class="lucide lucide-minus-icon lucide-minus"
                                    >
                                        <path d="M5 12h14"/>
                                    </svg>
                                </button>
                                <input 
                                    value="${product.quantity}"
                                    class="w-8 no-spinner text-center font-medium
                                    bg-transparent text-white" 
                                    type="number" min=0 />
                                <button
                                    onclick="increaseProductQuantity(${product.id})"
                                >
                                    <svg 
                                        xmlns="http://www.w3.org/2000/svg" 
                                        width="16" height="16" viewBox="0 0 24 24" 
                                        fill="none" stroke="currentColor" stroke-width="2" 
                                        stroke-linecap="round" stroke-linejoin="round" 
                                        class="lucide lucide-plus-icon lucide-plus"
                                    >
                                        <path d="M5 12h14"/><path d="M12 5v14"/>
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                    <button 
                        onclick="removeProductFromBasket(${product.id})"
                        class="absolute top-2 right-2"
                    >
                        <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        width="20" height="20" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2"
                        stroke-linecap="round" stroke-linejoin="round"
                        class="lucide lucide-trash2-icon lucide-trash-2"
                        >
                        <path d="M10 11v6"/><path d="M14 11v6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
                        <path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            `;
}

updateBasketView();
