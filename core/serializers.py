from rest_framework import serializers
from .models import *

# LO USAMOS PARA PODER TRANSFORMAR LOS DATOS DE PYTHON A DATOS JSON
class GeneroMusicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneroMusical
        fields = '__all__'

class ArtistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artista
        fields = '__all__'

class TipoLanzamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoLanzamiento
        fields = '__all__'

class LanzamientoSerializer(serializers.ModelSerializer):
    genero = GeneroMusicalSerializer(read_only=True)
    artista = ArtistaSerializer(read_only=True)
    tipoLanzamiento = TipoLanzamientoSerializer(read_only=True)

    class Meta:
        model = Lanzamiento
        fields = '__all__'