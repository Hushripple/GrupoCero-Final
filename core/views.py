from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.serializers import serialize
from rest_framework import viewsets
from .serializers import *
from rest_framework.renderers import JSONRenderer
import requests
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
import json
from django.http import JsonResponse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.lib import colors
from django.http import FileResponse
import string
import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
# Create your views here.

def get_artists_by_genre(request, genre):
    api_url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={genre}&api_key={settings.LASTFM_API_KEY}&format=json"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        artists = data.get('topartists', {}).get('artist', [])
        
        # Agregar paginación
        paginator = Paginator(artists, 10)  # Muestra 10 artistas por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'core/artistasapi/artists_by_genre.html', {'page_obj': page_obj, 'genre': genre})
    else:
        return render(request, 'core/artistasapi/artists_by_genre.html', {'error': 'No artists found for this genre', 'genre': genre})

#CARRITO
def carrito(request):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        aux = {
            'carrito': Carrito.objects.filter(usuario=request.user)
        }
    else:
        messages.error(request, '¡Por favor inicie sesión para comenzar a agregar productos al carrito!')
        aux = None
    return render(request, 'core/carrito.html', aux)

def agregar_producto_carrito(request, lanz_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        lanz = get_object_or_404(Lanzamiento, pk=lanz_id)
        if Carrito.objects.filter(usuario=request.user, producto=lanz):
            messages.error(request, '¡El lanzamiento ya está en el carrito!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            c = Carrito(
                usuario = request.user, 
                producto = lanz
                )
            c.save()
            messages.success(request, '¡Lanzamiento agregado correctamente!')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, '¡Debe haber iniciado sesión para agregar el lanzamiento al carrito!')
    return redirect(request.META.get('HTTP_REFERER'))

def eliminar_producto_carrito(request, lanz_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        lanz = get_object_or_404(Lanzamiento, pk=lanz_id)
        item = Carrito.objects.filter(usuario=request.user, producto=lanz)
        if item:
            item.delete()
        else:
            messages.error(request, '¡El lanzamiento no existe en el carrito!')
            return redirect('carrito')
    else:
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('carrito')

def cantidad_productos_carrito(request):
    if request.user.is_authenticated:
        try:
            contador = Carrito.objects.filter(usuario=request.user).count()
        except Exception as e:
            print(e)
            contador = 0
    else:
        contador = 0
    return contador

@csrf_exempt
@login_required
def registrar_pago(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        metodo_pago = data.get('metodo_pago')
        usuario = request.user
        lanzamientos_ids = data.get('lanzamientos_ids', [])

        historial_pago = HistorialPagosUsuario.objects.create(
            usuario=usuario,
            metodo_pago=metodo_pago
        )

        for lanz_id in lanzamientos_ids:
            lanzamiento = Lanzamiento.objects.get(id=lanz_id)
            historial_pago.lanzamientos_comprados.add(lanzamiento)

        historial_pago.save()

        # Limpiar el carrito después de registrar el pago
        Carrito.objects.filter(usuario=usuario).delete()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def historial_pagos(request):
    pagos = HistorialPagosUsuario.objects.filter(usuario=request.user)
    return render(request, 'historial_pagos.html', {'pagos': pagos})

@login_required
def generar_voucher(request, pago_id):
    pago = get_object_or_404(HistorialPagosUsuario, id=pago_id, usuario=request.user)

    # Formatear la fecha como string legible
    fecha_pago_str = pago.fecha_pago.strftime("%d/%m/%Y %H:%M:%S")

    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()

    # Configurar el canvas con el tamaño de página Letter (carta)
    p = canvas.Canvas(buffer, pagesize=letter)

    # Configurar dimensiones y márgenes
    width, height = letter
    left_margin = 50
    right_margin = width - 50
    top_margin = height - 50
    bottom_margin = 50

    # Dibujar el rectángulo de fondo con un color blanco (el fondo)
    p.setFillColorRGB(1, 1, 1)  # Blanco (RGB: 1, 1, 1)
    p.rect(left_margin, bottom_margin, width - 2 * left_margin, height - top_margin - bottom_margin, fill=1)

    # Configurar el color del borde (negro)
    p.setStrokeColorRGB(0, 0, 0)  # Negro (RGB: 0, 0, 0)
    p.setLineWidth(1)

    # Dibujar el borde exterior del voucher
    p.rect(left_margin, bottom_margin, width - 2 * left_margin, height - top_margin - bottom_margin)

    # Configurar el color del texto (negro)
    p.setFillColorRGB(0, 0, 0)  # Negro (RGB: 0, 0, 0)

    # Escribir el contenido del voucher dentro del margen
    p.setFont("Helvetica-Bold", 16)
    p.drawString(left_margin + 50, top_margin - 50, f"Voucher de Pago")
    p.setFont("Helvetica", 12)
    p.drawString(left_margin + 50, top_margin - 100, f"Usuario: {pago.usuario.username}")
    p.drawString(left_margin + 50, top_margin - 130, f"Fecha de Pago: {fecha_pago_str}")
    p.drawString(left_margin + 50, top_margin - 160, f"Método de Pago: {pago.metodo_pago}")
    p.drawString(left_margin + 50, top_margin - 190, "Lanzamientos Comprados:")
    y_position = top_margin - 220
    for lanzamiento in pago.lanzamientos_comprados.all():
        p.drawString(left_margin + 70, y_position, f"- {lanzamiento.nombreLanzamiento}")
        y_position -= 20

    # Guardar el canvas
    p.showPage()
    p.save()

    # Devolver el PDF como una FileResponse para descargar
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"voucher_pago_{pago_id}.pdf")

# METODOS PARA LISTAR DESDE EL API
def lanzamientosapi(request):
    response = requests.get('https://gc-d-final.vercel.app/api/lanzamiento/')
    lanzamientos = [lanz for lanz in response.json() if lanz['aprobado'] == 'aprobado']

    paginator = Paginator(lanzamientos, 5)  # Muestra 5 lanzamientos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'core/lanzamientosapi/index.html', context)

def artistasapi(request):
    response = requests.get('https://gc-d-final.vercel.app/api/artista/')
    artistas = response.json()

    # Pagina la respuesta de la API
    paginator = Paginator(artistas, 5)  # Muestra 5 artistas por página
    page_number = request.GET.get('page')  # Busca la página
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'core/artistasapi/index.html', context)

def lanzamientosdetalle(request, id):
    response = requests.get(f'https://gc-d-final.vercel.app/api/lanzamiento/{id}')
    lanzamientos = response.json()

    context = {
        'listaLanzObj': lanzamientos
    }

    return render(request, 'core/lanzamientosapi/detalle.html', context)


# UTILIZAMOS LOS VIEWSET PARA MANEJAR LAS SOLICITUDES TIPO HTTP (GET, POST, PUT, DELETE)
class GeneroMusicalViewSet(viewsets.ModelViewSet):
    queryset = GeneroMusical.objects.all().order_by('id')
    serializer_class = GeneroMusicalSerializer
    renderer_classes = [JSONRenderer]

class ArtistaViewSet(viewsets.ModelViewSet):
    queryset = Artista.objects.filter(aprobado='aprobado').order_by('id')
    serializer_class = ArtistaSerializer
    renderer_classes = [JSONRenderer]

class TipoLanzamientoViewSet(viewsets.ModelViewSet):
    queryset = TipoLanzamiento.objects.all().order_by('id')
    serializer_class = TipoLanzamientoSerializer
    renderer_classes = [JSONRenderer]

class LanzamientoViewSet(viewsets.ModelViewSet):
    queryset = Lanzamiento.objects.filter(aprobado='aprobado').order_by('id')
    serializer_class = LanzamientoSerializer
    renderer_classes = [JSONRenderer]

# Definir una función para verificar si el usuario pertenece al grupo administradores
def user_is_admin(user):
    return user.groups.filter(name='administradores').exists()

# Definir una función para verificar si el usuario pertenece al grupo miembros
def user_is_member(user):
    return user.groups.filter(name='miembros').exists()

def index (request):
    context = {
        'listaArtistas' : Artista.objects.filter(aprobado='aprobado')[:4],
        'listaLanzamientos' : Lanzamiento.objects.filter(aprobado='aprobado')[:4]
    }

    return render(request, 'core/index.html', context)

def account_locked(request):
    return render(request, 'core/account_locked.html')

def artistas (request):
    auxArtObj = {
        'listaArtObj' : Artista.objects.filter(aprobado='aprobado')
    }

    return render(request, 'core/artistas.html', auxArtObj)

def lanzamientos (request):
    auxLanzObj = {
        'listaLanzObj' : Lanzamiento.objects.filter(aprobado='aprobado')
    }

    return render(request, 'core/lanzamientos.html', auxLanzObj)

def loginmiembros (request):
    return render(request, 'core/miembros/loginMiembros.html')

@user_passes_test(user_is_member, login_url='loginmiembros')
def miembrosindex(request):
    return render(request, 'core/miembros/miembrosIndex.html')

@user_passes_test(user_is_member, login_url='loginmiembros')
def addtipolanzamientos (request):
    return render(request, 'core/miembros/tipoLanzamientos/crud/add.html')

@user_passes_test(user_is_member, login_url='loginmiembros')
def addgeneros (request):
    return render(request, 'core/miembros/generos/crud/add.html')

@user_passes_test(user_is_admin, login_url='loginadmins')
def adminsindex(request): 
    context = {
        'solicitudes' : Artista.objects.filter(aprobado='pendiente').values('id', 'fecha_solicitud', 'nombreArtista', 'aprobado'),
    }
    return render(request, 'core/admins/adminsIndex.html', context)

@user_passes_test(user_is_admin, login_url='loginadmins')
def adminSolicitudes(request):
    context = {
        'Artistas' : Artista.objects.filter(aprobado='pendiente'),
        'Lanzamientos' : Lanzamiento.objects.filter(aprobado='pendiente'),
        'Generos' : GeneroMusical.objects.filter(aprobado='pendiente'),
        'TiposLanzamientos' : TipoLanzamiento.objects.filter(aprobado='pendiente')
    }
    return render(request, 'core/admins/adminsSolicitudes.html', context)

@user_passes_test(user_is_admin, login_url='loginadmins')
def adminSolicitudesArtistas(request):
    id = request.GET.get('id')
    artista = Artista.objects.filter(id=id).first()
    context = {
        'Artista' : artista
    }
    return render(request, 'core/admins/adminsSolicitudesArtistas.html', context)

@user_passes_test(user_is_admin, login_url='loginadmin')
def adminSolicitudesLanzamientos (request):
    id = request.GET.get('id')
    lanzamiento = Lanzamiento.objects.filter(id=id).first()
    context = {
        'Lanzamiento' : lanzamiento
    }
    return render(request, 'core/admins/adminsSolicitudesLanzamientos.html', context)

@user_passes_test(user_is_admin, login_url='loginadmin')
def adminSolicitudesTipoLanzamientos (request):
    id = request.GET.get('id')
    print(id)
    tipolanzamiento = TipoLanzamiento.objects.filter(id=id).first()
    context = {
        'TipoLanzamiento' : tipolanzamiento
    }
    return render(request, 'core/admins/adminsSolicitudesTipoLanzamientos.html', context)

@user_passes_test(user_is_admin, login_url='loginadmin')
def adminSolicitudesGeneros (request):
    id = request.GET.get('id')
    genero = GeneroMusical.objects.filter(id=id).first()
    context = {
        'Genero' : genero
    }
    return render(request, 'core/admins/adminsSolicitudesGeneros.html', context)

@user_passes_test(user_is_admin, login_url='loginadmin')
def adminsaprobar (request):
    if request.method == 'POST':
        print(request.POST)
        id = request.POST.get('id')
        tipo = request.POST.get('tipo')
        estado = request.POST.get('aprobado')
        feedback = request.POST.get('feedback')

        match tipo:
            case 'artista':
                print(request.POST)
                artista = Artista.objects.filter(id=id).first()
                artista.aprobado = estado
                artista.feedback = feedback
                artista.save()
            case 'lanzamiento':
                print(request.POST)
                lanzamiento = Lanzamiento.objects.filter(id=id).first()
                lanzamiento.aprobado = estado
                lanzamiento.feedback = feedback
                lanzamiento.save()
            case 'genero':
                print(request.POST)
                genero = GeneroMusical.objects.filter(id=id).first()    
                genero.aprobado = estado
                genero.save()
            case 'TipoLanzamiento':
                print(request.POST)
                tipolanzamiento = TipoLanzamiento.objects.filter(id=id).first()
                tipolanzamiento.aprobado = estado
                tipolanzamiento.feedback = feedback
                tipolanzamiento.save()

        return redirect('adminsolicitudes')
    return render(request, 'adminsolicitudes')

def loginadmins (request):
    return render(request, 'core/admins/loginAdmins.html')

# LOGIN 

def logincliente(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.groups.filter(name='clientes').exists():
                login(request, user)
                return redirect('index')
            elif user.groups.filter(name='miembros').exists():
                messages.error(request, 'Solo los clientes pueden iniciar sesión en este sitio.')
                return redirect('index')
        else:
            messages.error(request, 'Credenciales de inicio de sesión incorrectas.')
            return redirect('index')

    return render(request, 'index')

def logout_view(request):
    logout(request)
    return redirect('index')  

def loginmiembro(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email=email)
            username = user.username
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.groups.filter(name='miembros').exists():
                    login(request, user)
                    return redirect('miembrosindex')
                elif user.groups.filter(name='clientes').exists():
                    messages.error(request, 'Solo los miembros pueden iniciar sesión en este sitio.')
                    return redirect('loginmiembros')
            else:
                messages.error(request, 'Credenciales de inicio de sesión incorrectas.')
                return redirect('loginmiembros')
        
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico.')
            return redirect('loginmiembros')
    
    return render(request, 'loginmiembros')

def loginadmin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.groups.filter(name='administradores').exists():
                login(request, user)
                return redirect('adminsindex') 
            elif user.groups.filter(name='clientes').exists():
                messages.error(request, 'Solo los administradores pueden iniciar sesión en este sitio.')
                return redirect('loginadmins')
            elif user.groups.filter(name='miembros').exists():
                messages.error(request, 'Solo los administradores pueden iniciar sesión en este sitio.')
        else:
            messages.error(request, 'Credenciales de inicio de sesión incorrectas.')
            return redirect('loginadmins')

    return render(request, 'loginadmins')  

# REGISTRO

def registercliente(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password_confirmation']

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('index')
        elif len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('index')
        elif len(username) < 3:
            messages.error(request, 'El nombre de usuario debe tener al menos 3 caracteres.')
            return redirect('index')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('index')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('index')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            cliente_group = Group.objects.get(name='clientes')
            user.groups.add(cliente_group)
            user.save()
            messages.success(request, 'Usuario creado correctamente')
            return redirect('index')

    return render(request, 'index')

# TIPO LANZAMIENTOS
@user_passes_test(user_is_member, login_url='loginmiembros')
def tipolanzamientosobjects(request):
    auxTipoObj = {
        'listaTipoObj' : TipoLanzamiento.objects.all()
    }

    return render(request, 'core/miembros/tipoLanzamientos/tipolanzamientosobjects.html', auxTipoObj)

@user_passes_test(user_is_member, login_url='loginmiembros')
def tipolanzamientosadd(request):
    aux = {
        'form': TipoLanzamientoForm()
    }

    if request.method == 'POST':
        formulario = TipoLanzamientoForm(request.POST)
        print(formulario.is_valid())
        if formulario.is_valid():
            formulario.save()
            aux['msj'] = "¡Tipo lanzamiento guardado correctamente!"
        else:
            aux['form'] = formulario
            aux['msj'] = "¡Error al guardar el tipo de lanzamiento!"

    return render(request, 'core/miembros/tipoLanzamientos/crud/add.html', aux)
@user_passes_test(user_is_member, login_url='loginmiembros')
def tipolanzamientosupdate(request, id):
    tipo = TipoLanzamiento.objects.get(id=id)

    if request.method == 'POST':
        formulario = TipoLanzamientoForm(data=request.POST, instance=tipo)
        if formulario.is_valid():
            formulario.save()
            return redirect('tipolanzamientosobjects')
    else:
        formulario = TipoLanzamientoForm(instance=tipo)

    return render(request, 'core/miembros/tipoLanzamientos/crud/update.html', {'form': formulario, 'tipo': tipo})

@user_passes_test(user_is_member, login_url='loginmiembros')
def tipolanzamientosdelete(request, id):
    tipo = TipoLanzamiento.objects.get(id=id)
    tipo.delete()
    
    return redirect(reverse('tipolanzamientosobjects'))

# ARTISTAS
@user_passes_test(user_is_member, login_url='loginmiembros')
def artistasobjects(request):
    auxArtObj = {
        'listaArtObj' : Artista.objects.all()
    }

    return render(request, 'core/miembros/artistas/artistasobjects.html', auxArtObj)

@user_passes_test(user_is_member, login_url='loginmiembros')
def artistasadd(request):
    aux = {
        'form': ArtistaForm()
    }

    if request.method == 'POST':
        formulario = ArtistaForm(request.POST, request.FILES) 
        if formulario.is_valid():
            formulario.save()
            aux['msj'] = "Artista guardado correctamente!"
        else:
            aux['form'] = formulario
            aux['msj'] = "¡Error al guardar el artistal!"

    return render(request, 'core/miembros/artistas/crud/add.html', aux)

@user_passes_test(user_is_member, login_url='loginmiembros')
def artistasupdate(request, id):
    artista = Artista.objects.get(id=id)

    if request.method == 'POST':
        formulario = ArtistaForm(data=request.POST, instance=artista)
        if formulario.is_valid():
            formulario.save()
            return redirect('artistasobjects')
    else:
        formulario = ArtistaForm(instance=artista)

    return render(request, 'core/miembros/artistas/crud/update.html', {'form': formulario, 'artista': artista})

@user_passes_test(user_is_member, login_url='loginmiembros')
def artistasdelete(request, id):
    artista = Artista.objects.get(id=id)
    artista.delete()
    
    return redirect(reverse('artistasobjects'))

# LANZAMIENTOS
@user_passes_test(user_is_member, login_url='loginmiembros')
def lanzamientosobjects(request):
    auxLanzObj = {
        'listaLanzObj' : Lanzamiento.objects.all()
    }

    return render(request, 'core/miembros/lanzamientos/lanzamientosobjects.html', auxLanzObj)

@user_passes_test(user_is_member, login_url='loginmiembros')
def lanzamientosadd(request):
    aux = {
        'form': LanzamientoForm()
    }

    if request.method == 'POST':
        formulario = LanzamientoForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            aux['msj'] = "Lanzamiento guardado correctamente!"
        else:
            aux['form'] = formulario
            aux['msj'] = "¡Error al guardar el lanzamiento!"

    return render(request, 'core/miembros/lanzamientos/crud/add.html', aux)

@user_passes_test(user_is_member, login_url='loginmiembros')
def lanzamientosupdate(request, id):
    lanzamientos = Lanzamiento.objects.get(id=id)

    if request.method == 'POST':
        formulario = LanzamientoForm(data=request.POST, instance=lanzamientos)
        if formulario.is_valid():
            formulario.save()
            return redirect('lanzamientosobjects')
    else:
        formulario = LanzamientoForm(instance=lanzamientos)

    return render(request, 'core/miembros/lanzamientos/crud/update.html', {'form': formulario, 'lanzamientos': lanzamientos})

@user_passes_test(user_is_member, login_url='loginmiembros')
def lanzamientosdelete(request, id):
    lanzamientos = Lanzamiento.objects.get(id=id)
    lanzamientos.delete()
    
    return redirect(reverse('lanzamientosobjects'))


# GÉNERO MUSICAL

@user_passes_test(user_is_member, login_url='loginmiembros')
def generosobjects(request):
    auxGenObj = {
        'listaGenObj' : GeneroMusical.objects.all()
    }

    return render(request, 'core/miembros/generos/generosobjects.html', auxGenObj)

@user_passes_test(user_is_member, login_url='loginmiembros')
def generosadd(request):
    aux = {
        'form': GeneroMusicalForm()
    }

    if request.method == 'POST':
        formulario = GeneroMusicalForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            aux['msj'] = "¡Género musical guardado correctamente!"
        else:
            aux['form'] = formulario
            aux['msj'] = "¡Error al guardar el género musical!"

    return render(request, 'core/miembros/generos/crud/add.html', aux)

@user_passes_test(user_is_member, login_url='loginmiembros')
def generosupdate(request, id):
    genero = GeneroMusical.objects.get(id=id)

    if request.method == 'POST':
        formulario = GeneroMusicalForm(data=request.POST, instance=genero)
        if formulario.is_valid():
            formulario.save()
            return redirect('generosobjects')  # Redirige a la página de géneros después de la edición
    else:
        formulario = GeneroMusicalForm(instance=genero)

    return render(request, 'core/miembros/generos/crud/update.html', {'form': formulario, 'genero': genero})

@user_passes_test(user_is_member, login_url='loginmiembros')
def generosdelete(request, id):
    genero = GeneroMusical.objects.get(id=id)
    genero.delete()
    
    return redirect(reverse('generosobjects'))

# ADMINS

@user_passes_test(user_is_admin, login_url='loginadmins')
def registermiembro(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password_confirmation']

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('adminsindex')
        elif len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('adminsindex')
        elif len(username) < 3:
            messages.error(request, 'El nombre de usuario debe tener al menos 3 caracteres.')
            return redirect('adminsindex')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('adminsindex')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('adminsindex')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            miembro_group = Group.objects.get(name='miembros')
            user.groups.add(miembro_group)
            user.save()
            messages.success(request, 'Cuenta de miembro creada correctamente')
            return redirect('adminsindex')

    return render(request, 'adminsindex')


