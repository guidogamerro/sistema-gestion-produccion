from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import PerfilUsuario
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Crear perfil de usuario en estado 'pendiente'
            PerfilUsuario.objects.create(user=user, estado='pendiente')
            messages.success(request, 'Registro exitoso. Espera la aprobación del administrador.')
            return redirect('login')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registrar.html', {'form': form})

@login_required
def aprobar_usuarios(request):
    if not request.user.is_staff:
        return redirect('login')
    
    usuarios_pendientes = PerfilUsuario.objects.filter(estado='pendiente')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        accion = request.POST.get('accion')
        perfil = PerfilUsuario.objects.get(id=usuario_id)

        if accion == 'aprobar':
            perfil.estado = 'aprobado'
            messages.success(request, f'Usuario {perfil.user.username} aprobado.')
        elif accion == 'rechazar':
            perfil.estado = 'rechazado'
            messages.warning(request, f'Usuario {perfil.user.username} rechazado.')

        perfil.save()
        return redirect('usuarios:aprobar_usuarios')

    return render(request, 'usuarios/aprobar_usuarios.html', {'usuarios_pendientes': usuarios_pendientes})


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'


@user_passes_test(lambda u: u.is_staff, login_url='/home/')
def gestion_usuarios(request):
    # Obtiene todos los usuarios registrados
    usuarios = PerfilUsuario.objects.filter(estado='aprobado')
    usuarios2 = User.objects.filter(is_staff=True)
    
    # Filtrar usuarios pendientes de aprobación
    #pendientes = PerfilUsuario.objects.filter(estado='pendiente')

    ctx = {'usuarios': usuarios, 'usuarios2': usuarios2}
    
    return render(request, 'usuarios/gestion_usuarios.html', ctx)