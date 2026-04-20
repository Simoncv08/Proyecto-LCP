from .models import DocumentoLegal

def documentos_legales(request):
    terminos = DocumentoLegal.objects.filter(tipo='terminos').order_by('-fecha').first()
    privacidad = DocumentoLegal.objects.filter(tipo='privacidad').order_by('-fecha').first()

    return {
        'terminos_actual': terminos,
        'privacidad_actual': privacidad,
    }