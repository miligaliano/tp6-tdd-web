import re
from datetime import date

DIAS_ABIERTOS = [1, 2, 3, 4, 5, 6]  # martes a domingo


def validar_email(email):
    """Valida formato de email básico."""
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(patron, email))


def validar_usuario_registrado(usuario):
    """Devuelve True si el usuario está registrado y su mail es válido."""
    return usuario.get("registrado", False) and validar_email(usuario.get("email", ""))


def validar_fecha_visita(fecha_visita):
    """Devuelve True si la fecha es hoy o futura y el parque está abierto."""
    return fecha_visita >= date.today() and fecha_visita.weekday() in DIAS_ABIERTOS


def validar_cantidad_entradas(cantidad):
    """Devuelve True si la cantidad está entre 1 y 10."""
    return 1 <= cantidad <= 10


def validar_forma_pago(forma_pago):
    """Devuelve True si la forma de pago es válida."""
    return forma_pago in ["efectivo", "tarjeta"]


def calcular_monto_total(cantidad, tipo_pase="regular"):
    """Calcula el monto total en base al tipo de pase."""
    precio_base = 10000
    if tipo_pase == "VIP":
        precio_base *= 1.5
    return cantidad * precio_base


def procesar_compra(usuario, fecha, cantidad, edades, tipo_pase, forma_pago):
    """Procesa la compra de entradas."""
    if not validar_usuario_registrado(usuario):
        return {"ok": False, "mensaje": "Debe estar registrado y tener un email válido."}

    if not validar_fecha_visita(fecha):
        return {"ok": False, "mensaje": "La fecha no es válida o el parque está cerrado."}

    if not validar_cantidad_entradas(cantidad):
        return {"ok": False, "mensaje": "Cantidad de entradas inválida (máx. 10)."}

    if not edades or len(edades) != cantidad:
        return {"ok": False, "mensaje": "Debe indicar la edad de cada visitante."}

    if not validar_forma_pago(forma_pago):
        return {"ok": False, "mensaje": "Debe seleccionar una forma de pago válida."}

    total = calcular_monto_total(cantidad, tipo_pase)
    mensaje = f"Compra confirmada: {cantidad} entradas para el {fecha} por ${total}."

    if forma_pago == "tarjeta":
        mensaje += " Redirigiendo a Mercado Pago..."
    else:
        mensaje += " Pago en boletería."

    return {"ok": True, "mensaje": mensaje}
