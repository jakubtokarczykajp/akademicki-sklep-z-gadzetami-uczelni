"""
Context processors dla szablonów Django.
"""
from django.contrib.auth.models import AnonymousUser


def user_wishlists(request):
    """
    Dodaje wishlists zalogowanego użytkownika do contextu.
    """
    wishlists = []
    
    if request.user.is_authenticated:
        try:
            # Pobieramy wishlists użytkownika
            from oscar.core.loading import get_model
            WishList = get_model('wishlists', 'WishList')
            wishlists = WishList.objects.filter(owner=request.user)
        except Exception as e:
            print(f"Error fetching wishlists: {e}")
    
    return {
        'user_wishlists': wishlists,
    }
