from django.urls import path, include
from .views import *
from rest_framework import routers

# CONFIGURAMOS LAS URLS PARA EL API
router = routers.DefaultRouter()
router.register('generomusical', GeneroMusicalViewSet)
router.register('artista', ArtistaViewSet)
router.register('tipolanzamiento', TipoLanzamientoViewSet)
router.register('lanzamiento', LanzamientoViewSet)

urlpatterns = [
    path('', index, name="index"),
    path('artistas/', artistas, name="artistas"), 
    path('adminsindex/', adminsindex, name="adminsindex"),
    path('adminsolicitudes/', adminSolicitudes, name="adminsolicitudes"),
    path('adminsolicitudesartistas/', adminSolicitudesArtistas, name="adminsolicitudesartistas"),
    path('adminsolicitudeslanzamientos/', adminSolicitudesLanzamientos, name="adminsolicitudeslanzamientos"),
    path('adminsolicitudestipolanzamientos/', adminSolicitudesTipoLanzamientos, name="adminsolicitudestipolanzamientos"),
    path('adminsolicitudesgeneros/', adminSolicitudesGeneros, name="adminsolicitudesgeneros"),
    path('adminsaprobar/', adminsaprobar, name="adminsaprobar"),    
    path('loginadmins/', loginadmins, name="loginadmins"),
    path('loginadmin/', loginadmin, name="loginadmin"),
    path('lanzamientos/', lanzamientos, name="lanzamientos"), 
    path('loginmiembros/', loginmiembros, name="loginmiembros"),
    path('miembrosindex/', miembrosindex, name="miembrosindex"),
    path('login/', logincliente, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', registercliente, name='registercliente'),
    path('registermiembro/', registermiembro, name='registermiembro'),
    path('loginmiembro/', loginmiembro, name='loginmiembro'),
    path('addtipolanzamientos/', addtipolanzamientos, name='addtipolanzamientos'),
    path('generosobjects/', generosobjects, name='generosobjects'),
    path('generosadd/', generosadd, name='generosadd'),
    path('generosdelete/<int:id>/', generosdelete, name='generosdelete'),
    path('generosupdate/<int:id>/', generosupdate, name='generosupdate'),
    path('artistasobjects/', artistasobjects, name='artistasobjects'),
    path('artistasadd/', artistasadd, name='artistasadd'),
    path('artistasdelete/<int:id>/', artistasdelete, name='artistasdelete'),
    path('artistasupdate/<int:id>/', artistasupdate, name='artistasupdate'),
    path('tipolanzamientosobjects/', tipolanzamientosobjects, name='tipolanzamientosobjects'),
    path('tipolanzamientossadd/', tipolanzamientosadd, name='tipolanzamientosadd'),
    path('tipolanzamientosdelete/<int:id>/', tipolanzamientosdelete, name='tipolanzamientosdelete'),
    path('tipolanzamientosupdate/<int:id>/', tipolanzamientosupdate, name='tipolanzamientosupdate'),
    path('lanzamientosobjects/', lanzamientosobjects, name='lanzamientosobjects'),
    path('lanzamientosadd/', lanzamientosadd, name='lanzamientosadd'),
    path('lanzamientosdelete/<int:id>/', lanzamientosdelete, name='lanzamientosdelete'),
    path('lanzamientosupdate/<int:id>/', lanzamientosupdate, name='lanzamientosupdate'),
    path('account_locked/', account_locked, name='account_locked'),
    path('carrito/', carrito, name='carrito'),
    path('carrito/add/<int:lanz_id>/', agregar_producto_carrito, name="carritoadd"),
    path('carrito/contadordeproductos/', cantidad_productos_carrito, name="carritocontador"),
    path('carrito/delete/<int:lanz_id>/', eliminar_producto_carrito, name="carritodelete"),
    # API
    path('api/', include(router.urls)),
    path('lanzamientosapi/', lanzamientosapi, name='lanzamientosapi'),
    path('lanzamientosdetalle/<int:id>/', lanzamientosdetalle, name='lanzamientosdetalle'),
    path('artistasapi/', artistasapi, name='artistasapi'),

    path('registrar_pago/', registrar_pago, name='registrar_pago'),
    path('historial_pagos/', historial_pagos, name='historial_pagos'),
    path('generar_voucher/<int:pago_id>/', generar_voucher, name='generar_voucher'),

    path('genre/<str:genre>/', get_artists_by_genre, name='get_artists_by_genre'),

]
