from .views import cantidad_productos_carrito

def carrito(request):
    return {'cantidad': cantidad_productos_carrito(request)}