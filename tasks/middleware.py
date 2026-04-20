from django.shortcuts import redirect
from django.urls import resolve
from .models import DocumentoLegal, Profile

class VerificarTerminosMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            profile, _ = Profile.objects.get_or_create(user=request.user)

            terminos = DocumentoLegal.objects.filter(tipo='terminos').order_by('-fecha').first()
            privacidad = DocumentoLegal.objects.filter(tipo='privacidad').order_by('-fecha').first()

            if (
                (terminos and profile.version_terminos != terminos.version) or
                (privacidad and profile.version_privacidad != privacidad.version)
            ):

                current_url = resolve(request.path_info).url_name

                rutas_permitidas = [
                    'aceptar_terminos',
                    'logout',
                    'admin:index',
                    'admin:login'
                ]

                if current_url not in rutas_permitidas:
                    return redirect('aceptar_terminos')

        return self.get_response(request)