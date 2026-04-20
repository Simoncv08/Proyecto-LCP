from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TransaccionForm, EventoForm, CustomAuthForm, CustomUserCreationForm, EstudianteForm, UsuarioForm
from .models import Transaccion, Eventos, Producto, DetalleTransaccion, Estudiante, Profile, DocumentoLegal
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone

import openpyxl


def home(request):
    return render(request, 'home.html', {})


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': CustomUserCreationForm})

    if request.POST['password1'] == request.POST['password2']:
        try:
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1']
            )
            user.save()

            # ❌ QUITAMOS ESTO
            # login(request, user)

            return redirect('tasks')  # o '/tasks'

        except IntegrityError:
            return render(request, 'signup.html', {
                'form': CustomUserCreationForm,
                'error': 'Usuario ya existente.'
            })

    return render(request, 'signup.html', {
        'form': CustomUserCreationForm,
        'error': 'Contraseñas no coinciden.'
    })


@login_required
def tasks(request):
    transacciones = Transaccion.objects.all()
    eventos = Eventos.objects.all()

    evento = request.GET.get('evento')
    if evento:
        transacciones = transacciones.filter(evento_id=evento)

    grado_seccion = request.GET.get('grado_seccion')
    if grado_seccion:
        try:
            grado = int(grado_seccion[:-1])
            seccion = grado_seccion[-1]
            transacciones = transacciones.filter(grado=grado, seccion=seccion)
        except:
            pass

    estudiante = request.GET.get('estudiante')
    if estudiante:
        transacciones = transacciones.filter(
            estudiante__nombre__icontains=estudiante)

    recaudador = request.GET.get('recaudador')
    if recaudador:
        transacciones = transacciones.filter(
            usuario__username__icontains=recaudador)

    total = transacciones.aggregate(total=Sum('monto'))['total'] or 0

    opciones_grado_seccion = []
    for g in range(1, 13):
        for s in ['A', 'B']:
            opciones_grado_seccion.append(f"{g}{s}")

    return render(request, 'tasks.html', {
        'transacciones': transacciones,
        'eventos': eventos,
        'total_recaudado': total,
        'opciones_grado_seccion': opciones_grado_seccion
    })


@login_required
def create_task(request):
    if request.method == 'GET':
        form = TransaccionForm()
        form.fields['estudiante'].queryset = Estudiante.objects.none()
        return render(request, 'create_task.html', {
            'form': TransaccionForm(),
            'range_grados': range(1, 12)})
    else:
        try:
            form = TransaccionForm(request.POST)
            form.fields['estudiante'].queryset = Estudiante.objects.all()
            if form.is_valid():
                nuevaTransaccion = form.save(commit=False)
                nuevaTransaccion.usuario = request.user
                nuevaTransaccion.grado = nuevaTransaccion.estudiante.grado
                nuevaTransaccion.seccion = nuevaTransaccion.estudiante.seccion

                evento = nuevaTransaccion.evento
                total = 0
                hay_productos = False

                for key, value in request.POST.items():
                    if key.startswith("producto_"):
                        partes = key.split("_")
                        if len(partes) == 2 and partes[1].isdigit():
                            cantidad = int(value)
                            if cantidad > 0:
                                hay_productos = True
                                producto_id = partes[1]
                                producto = Producto.objects.get(id=producto_id)
                                total += producto.precio * cantidad

                nuevaTransaccion.monto = evento.precio_base + total
                nuevaTransaccion.save()

                if hay_productos:
                    for key, value in request.POST.items():
                        if key.startswith("producto_"):
                            cantidad = int(value)
                            if cantidad > 0:
                                producto_id = key.split("_")[1]
                                producto = Producto.objects.get(id=producto_id)
                                DetalleTransaccion.objects.create(
                                    transaccion=nuevaTransaccion,
                                    producto=producto,
                                    cantidad=cantidad
                                )

                return redirect('tasks')
            else:
                return render(request, 'create_task.html', {
                    'form': form, 'error': 'Formulario inválido'})
        except Exception as e:
            return render(request, 'create_task.html', {
                'form': TransaccionForm(), 'error': f'Error: {str(e)}'})


@login_required
@user_passes_test(lambda u: u.is_staff)
def events(request):
    eventos = Eventos.objects.all()
    return render(request, 'events.html', {'eventos': eventos})


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_event(request):
    if request.method == 'GET':
        return render(request, 'create_event.html', {'form': EventoForm()})
    else:
        try:
            form = EventoForm(request.POST)
            if form.is_valid():
                evento = form.save()
                contador = 0
                while True:
                    nombre = request.POST.get(f'producto_nombre_{contador}')
                    precio = request.POST.get(f'producto_precio_{contador}')
                    if not nombre:
                        break
                    if nombre and precio:
                        Producto.objects.create(
                            evento=evento, nombre=nombre, precio=int(precio))
                    contador += 1
                return redirect('events')
            else:
                return render(request, 'create_event.html', {
                    'form': form, 'error': 'Formulario inválido'})
        except Exception as e:
            return render(request, 'create_event.html', {
                'form': EventoForm(), 'error': str(e)})


@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': CustomAuthForm})

    user = authenticate(
        request,
        username=request.POST['username'],
        password=request.POST['password']
    )

    if user is None:
        return render(request, 'signin.html', {
            'form': CustomAuthForm,
            'error': 'Usuario y/o Contraseña incorrectas'
        })

    profile, _ = Profile.objects.get_or_create(user=user)

    terminos = DocumentoLegal.objects.filter(tipo='terminos').order_by('-fecha').first()
    privacidad = DocumentoLegal.objects.filter(tipo='privacidad').order_by('-fecha').first()

    if (
        (terminos and profile.version_terminos != terminos.version) or
        (privacidad and profile.version_privacidad != privacidad.version)
    ):
        login(request, user)  # importante: iniciar sesión antes de redirigir
        return redirect('aceptar_terminos')

    login(request, user)
    return redirect('tasks')

    # LOGIN
    login(request, user)

    # Obtener profile
    profile, _ = Profile.objects.get_or_create(user=user)

    # Obtener términos actuales
    terminos_actual = DocumentoLegal.objects.order_by('-fecha').first()

    # SI NO HA ACEPTADO ESTA VERSIÓN
    if terminos_actual and profile.version_terminos != terminos_actual.version:
        return redirect('aceptar_terminos')

    return redirect('tasks')


@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Eventos, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        return redirect('events')

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_event(request, evento_id):
    evento = get_object_or_404(Eventos, id=evento_id)
    productos = Producto.objects.filter(evento=evento)

    if request.method == 'GET':
        return render(request, 'edit_event.html', {
            'form': EventoForm(instance=evento), 'productos': productos})
    else:
        try:
            form = EventoForm(request.POST, instance=evento)
            if form.is_valid():
                evento = form.save()
                for producto in productos:
                    nombre = request.POST.get(f'nombre_{producto.id}')
                    precio = request.POST.get(f'precio_{producto.id}')
                    if request.POST.get(f'eliminar_{producto.id}'):
                        producto.delete()
                        continue
                    if nombre and precio:
                        producto.nombre = nombre
                        producto.precio = int(precio)
                        producto.save()
                contador = 0
                while True:
                    nombre = request.POST.get(f'producto_nombre_{contador}')
                    precio = request.POST.get(f'producto_precio_{contador}')
                    if not nombre:
                        break
                    if nombre and precio:
                        Producto.objects.create(
                            evento=evento, nombre=nombre, precio=int(precio))
                    contador += 1
                return redirect('events')
            else:
                return render(request, 'edit_event.html', {
                    'form': form, 'productos': productos,
                    'error': 'Formulario inválido'})
        except Exception as e:
            return render(request, 'edit_event.html', {
                'form': EventoForm(instance=evento),
                'productos': productos, 'error': str(e)})

@login_required
def productos_por_evento(request, evento_id):
    productos = Producto.objects.filter(evento_id=evento_id)
    evento = Eventos.objects.get(id=evento_id)
    data = {
        "productos": [
            {'id': p.id, 'nombre': p.nombre, 'precio': p.precio}
            for p in productos
        ],
        "precio_base": evento.precio_base
    }
    return JsonResponse(data)


@login_required
def estudiantes(request):
    estudiantes = Estudiante.objects.all().order_by('grado', 'seccion', 'nombre')
    return render(request, 'estudiantes.html', {'estudiantes': estudiantes})


@login_required
def create_estudiante(request):
    if request.method == 'GET':
        return render(request, 'create_estudiante.html', {'form': EstudianteForm()})
    else:
        try:
            form = EstudianteForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('estudiantes')
            return render(request, 'create_estudiante.html', {
                'form': form, 'error': 'Datos inválidos'})
        except Exception as e:
            return render(request, 'create_estudiante.html', {
                'form': EstudianteForm(), 'error': str(e)})


@login_required
def estudiantes_filtrados(request):
    grado = request.GET.get('grado')
    seccion = request.GET.get('seccion')

    qs = Estudiante.objects.all().order_by('nombre')
    if grado:
        qs = qs.filter(grado=grado)
    if seccion:
        qs = qs.filter(seccion=seccion)

    data = list(qs.values('id', 'nombre', 'grado', 'seccion'))
    return JsonResponse(data, safe=False)


@login_required
@user_passes_test(lambda u: u.is_staff)
def importar_estudiantes(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if not archivo:
            return render(request, 'importar_estudiantes.html', {
                'error': 'No se subió ningún archivo.'
            })

        if not archivo.name.endswith('.xlsx'):
            return render(request, 'importar_estudiantes.html', {
                'error': 'El archivo debe ser .xlsx'
            })

        try:
            wb = openpyxl.load_workbook(archivo)
            ws = wb.active

            creados  = 0
            omitidos = 0

            for fila in ws.iter_rows(min_row=2, values_only=True):  # min_row=2 salta el encabezado
                nombre  = fila[0]
                grado   = fila[1]
                seccion = fila[2]

                # Saltar filas vacías o incompletas
                if not nombre or not grado or not seccion:
                    omitidos += 1
                    continue

                # Evitar duplicados por nombre + grado + sección
                existe = Estudiante.objects.filter(
                    nombre=str(nombre).strip(),
                    grado=int(grado),
                    seccion=str(seccion).strip().upper()
                ).exists()

                if existe:
                    omitidos += 1
                    continue

                Estudiante.objects.create(
                    nombre=str(nombre).strip(),
                    grado=int(grado),
                    seccion=str(seccion).strip().upper()
                )
                creados += 1

            return render(request, 'importar_estudiantes.html', {
                'exito': f'Importación completada: {creados} estudiantes creados, {omitidos} omitidos.'
            })

        except Exception as e:
            return render(request, 'importar_estudiantes.html', {
                'error': f'Error al leer el archivo: {str(e)}'
            })

    return render(request, 'importar_estudiantes.html', {})


@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    if request.method == 'POST':
        estudiante.delete()
    return redirect('estudiantes')


@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == 'GET':
        return render(request, 'editar_estudiante.html', {
            'form': EstudianteForm(instance=estudiante),
            'estudiante': estudiante
        })
    else:
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            return redirect('estudiantes')
        return render(request, 'editar_estudiante.html', {
            'form': form,
            'estudiante': estudiante,
            'error': 'Datos inválidos'
        })
    
def aceptar_terminos(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    profile = request.user.profile

    if profile.acepta_terminos and profile.acepta_privacidad:
        return redirect('tasks')

    if request.method == "POST":
        if request.POST.get("terminos") and request.POST.get("privacidad"):
            profile.acepta_terminos = True
            profile.acepta_privacidad = True
            profile.save()
            return redirect('tasks')

        return render(request, 'aceptar_terminos.html', {
            'error': 'Debes aceptar ambos para continuar'
        })

    return render(request, 'aceptar_terminos.html')

def aceptar_terminos(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    profile = request.user.profile

    terminos = DocumentoLegal.objects.filter(tipo='terminos').order_by('-fecha').first()
    privacidad = DocumentoLegal.objects.filter(tipo='privacidad').order_by('-fecha').first()

    if request.method == 'POST':
        if request.POST.get("terminos") and request.POST.get("privacidad"):

            if terminos:
                profile.version_terminos = terminos.version

            if privacidad:
                profile.version_privacidad = privacidad.version

            profile.fecha_aceptacion = timezone.now()
            profile.save()

            return redirect('tasks')

    return render(request, 'aceptar_terminos.html', {
        'terminos': terminos,
        'privacidad': privacidad
    })

def base_context(request):
    return {
        "terminos_actual": DocumentoLegal.objects.filter(tipo="terminos").order_by("-version").first(),
        "privacidad_actual": DocumentoLegal.objects.filter(tipo="privacidad").order_by("-version").first(),
    }

@login_required
@user_passes_test(lambda u: u.is_staff)
def mora_view(request):
    eventos = Eventos.objects.all()
    grados = range(1, 12)

    evento_id = request.GET.get('evento')
    grado = request.GET.get('grado')
    seccion = request.GET.get('seccion')

    no_pagaron = None
    evento = None

    if evento_id:
        evento = get_object_or_404(Eventos, id=evento_id)

        pagaron_ids = Transaccion.objects.filter(
            evento=evento
        ).values_list('estudiante_id', flat=True)

        no_pagaron = Estudiante.objects.exclude(id__in=pagaron_ids)

        # 🔽 FILTROS
        if grado:
            no_pagaron = no_pagaron.filter(grado=grado)

        if seccion:
            no_pagaron = no_pagaron.filter(seccion=seccion)

    return render(request, 'mora.html', {
        'eventos': eventos,
        'no_pagaron': no_pagaron,
        'evento': evento,
        'grado': grado,
        'seccion': seccion,
        'grados': grados,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def usuarios_view(request):
    usuarios = User.objects.filter(is_staff=False, is_superuser=False)
    return render(request, 'usuarios.html', {'usuarios': usuarios})

@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(
        User,
        id=user_id,
        is_superuser=False,
        is_staff=False
    )

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)

            nueva_password = form.cleaned_data.get("nueva_password")
            if nueva_password:
                user.set_password(nueva_password)

            user.save()
            return redirect('usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form})