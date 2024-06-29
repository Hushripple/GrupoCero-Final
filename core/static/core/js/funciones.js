document.addEventListener("DOMContentLoaded", function () {
    // Seleccionar todos los botones de eliminar con la clase carrito
    var botonesCarrito = document.querySelectorAll('.carrito');
    botonesCarrito.forEach(function (boton) {
        boton.addEventListener('click', function () {
            var url = boton.getAttribute('data-url');
            if (confirm("¿Estás seguro de que quieres eliminar este producto de tu carrito?")) {
                window.location.href = url;
            }
        });
    });
});