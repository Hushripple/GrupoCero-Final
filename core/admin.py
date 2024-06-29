from django.contrib import admin
from .models import *
from django.contrib.admin import ModelAdmin
from admin_confirm import AdminConfirmMixin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

# Register your models here.

class GeneroMusicalAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_change = True
    confirmation_fields = ['nombreGenero', 'aprobado', 'fecha_solicitud', 'feedback']

class TipoLanzamientoAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_change = True
    confirmation_fields = ['nombreTipo', 'aprobado', 'fecha_solicitud', 'feedback']

class ArtistaAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_change = True
    confirmation_fields = ['nombreArtista', 'fecha_nacimiento', 'biografia', 'imagen',
                        'aprobado', 'fecha_solicitud', 'feedback']
    
class LanzamientoAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_change = True
    confirmation_fields = ['tipoLanzamiento', 'nombreLanzamiento', 'artista', 'fechaLanzamiento',
                        'genero', 'descripcionLanzamiento', 'precio', 'imagen', 'aprobado',
                        'fecha_solicitud', 'feedback']

admin.site.register(TipoLanzamiento, TipoLanzamientoAdmin)
admin.site.register(Lanzamiento, LanzamientoAdmin)
admin.site.register(GeneroMusical, GeneroMusicalAdmin)
admin.site.register(Artista, ArtistaAdmin)
admin.site.register(Carrito)