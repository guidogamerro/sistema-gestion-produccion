from django.shortcuts import redirect
from .models import PerfilUsuario

class BloquearUsuariosNoAprobadosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            perfil = PerfilUsuario.objects.filter(user=request.user).first()
            if perfil and perfil.estado != 'aprobado':
                return redirect('espera_aprobacion')

        response = self.get_response(request)
        return response