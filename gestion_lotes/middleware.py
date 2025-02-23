from django.shortcuts import redirect
from django.urls import reverse

class ProtegerGestionLotesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/gestion_lotes/') and not request.user.is_authenticated:
            return redirect(reverse('login'))  # Redirige al login si no está autenticado

        response = self.get_response(request)
        return response