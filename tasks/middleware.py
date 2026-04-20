from django.shortcuts import redirect
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

                rutas_permitidas = [
                    '/aceptar-terminos/',
                    '/logout/',
                    '/admin/',
                ]

                if not any(request.path.startswith(r) for r in rutas_permitidas):
                    return redirect('aceptar_terminos')

        return self.get_response(request)