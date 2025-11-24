from django.shortcuts import render

def home(request):
    # przykładowe dane
    items = [
        {"id": "101", "name": "Kubek AJP", "image": "theme/images/mug.png", "price": '20', "promotion": 'false', "discount": '0'},
        {"id": "102", "name": "Bluza Anonymous", "image": "theme/images/bluza_ajp_it.png", "price": '120', "promotion": 'false', "discount": '0'},
        {"id": "103", "name": "Bluza AIR", "image": "theme/images/bluza_ajp_air.png", "price": '120', "promotion": 'false', "discount": '0'},
        {"id": "104", "name": "Bluza WT", "image": "theme/images/bluza_wt.png", "price": '100', "promotion": 'true', "discount": '20', "discountedPrice": '80'},
        {"id": "105", "name": "Zestaw biurowy", "image": "theme/images/akcesoria_ajp.png", "price": '100', "promotion": 'false', "discount": '0'},
        {"id": "106", "name": "Koszulka AJP", "image": "theme/images/koszulka_ajp.png", "price": '50', "promotion": 'false', "discount": '0'},
        {"id": "101", "name": "Kubek AJP", "image": "theme/images/mug.png", "price": '20', "promotion": 'false', "discount": '0'},
        {"id": "102", "name": "Bluza Anonymous", "image": "theme/images/bluza_ajp_it.png", "price": '120', "promotion": 'false', "discount": '0'},
        {"id": "103", "name": "Bluza AIR", "image": "theme/images/bluza_ajp_air.png", "price": '120', "promotion": 'false', "discount": '0'},
        {"id": "104", "name": "Bluza WT", "image": "theme/images/bluza_wt.png", "price": '20', "promotion": 'false', "discount": '0'},
        {"id": "105", "name": "Zestaw biurowy", "image": "theme/images/akcesoria_ajp.png", "price": '100', "promotion": 'false', "discount": '0'},
        {"id": "106", "name": "Koszulka AJP", "image": "theme/images/koszulka_ajp.png", "price": '50', "promotion": 'false', "discount": '0'},
    ]

    return render(request, 'home.html', {'items': items})
