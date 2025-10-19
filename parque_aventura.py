import re
from datetime import date
from database import buscar_usuario_por_email

# ------------------------------------------------------------------------
# CLASE DE CONFIGURACIÓN
# ------------------------------------------------------------------------


class ConfiguracionParque:
    """Centraliza las reglas y valores del parque para fácil mantenimiento."""
    DIAS_ABIERTOS = [0, 1, 2, 3, 4,
                     5]  # Lunes a Sábado (Domingo = 6, está cerrado)
    PRECIOS = {
        "regular": 10000,
        "VIP": 15000
    }
    CANTIDAD_MAX_ENTRADAS = 10
    CANTIDAD_MIN_ENTRADAS = 1

# ------------------------------------------------------------------------
# CLASES PRINCIPALES
# ------------------------------------------------------------------------


class Usuario:
    """Representa a un usuario del sistema."""

    def __init__(self, email, registrado=False):
        self.email = email
        self.registrado = registrado

    @classmethod
    def desde_la_sesion(cls, email):
        """Crea un usuario a partir de datos de sesión, verificando si existe en la BD."""
        if not email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return cls(email, False)

        existe = buscar_usuario_por_email(email) is not None
        return cls(email, existe)


class Compra:
    """Gestiona el proceso de compra de entradas."""

    def __init__(self, usuario_logueado: Usuario, fecha_visita, cantidad, edades, tipo_pase, forma_pago):
        self.usuario = usuario_logueado
        self.fecha_visita = fecha_visita
        self.cantidad = cantidad
        self.edades = edades
        self.tipo_pase = tipo_pase
        self.forma_pago = forma_pago
        self.errores = []

    def _validar_usuario(self):
        if not self.usuario or not self.usuario.registrado:
            self.errores.append(
                "El usuario no es válido o no está registrado.")

    def _validar_fecha(self):
        if not (self.fecha_visita >= date.today() and self.fecha_visita.weekday() in ConfiguracionParque.DIAS_ABIERTOS):
            self.errores.append(
                "La fecha no es válida o el parque está cerrado.")

    def _validar_cantidad(self):
        min_entradas = ConfiguracionParque.CANTIDAD_MIN_ENTRADAS
        max_entradas = ConfiguracionParque.CANTIDAD_MAX_ENTRADAS
        if not (min_entradas <= self.cantidad <= max_entradas):
            self.errores.append(
                f"Cantidad de entradas inválida (debe ser entre {min_entradas} y {max_entradas}).")

    def _validar_edades(self):
        if not self.edades or len(self.edades) != self.cantidad:
            self.errores.append("Debe indicar la edad de cada visitante.")

    def _validar_forma_pago(self):
        if self.forma_pago not in ["efectivo", "tarjeta"]:
            self.errores.append("Debe seleccionar una forma de pago válida.")

    def es_valida(self):
        """Ejecuta todas las validaciones y devuelve True si no hay errores."""
        self.errores = []
        self._validar_usuario()
        self._validar_fecha()
        self._validar_cantidad()
        self._validar_edades()
        self._validar_forma_pago()
        return not self.errores

    def calcular_monto_total(self):
        """Calcula el monto total en base al tipo de pase y la configuración."""
        precio_unitario = ConfiguracionParque.PRECIOS.get(self.tipo_pase, 0)
        return self.cantidad * precio_unitario

    def procesar(self):
        """Procesa la compra si todas las validaciones son correctas."""
        if not self.es_valida():
            return {"ok": False, "mensaje": " ".join(self.errores)}

        total = self.calcular_monto_total()
        mensaje = f"Compra confirmada para {self.usuario.email}: {self.cantidad} entradas para el {self.fecha_visita} por ${total}."

        if self.forma_pago == "tarjeta":
            mensaje += " Redirigiendo a Mercado Pago..."
        else:
            mensaje += " Pago en boletería."

        return {"ok": True, "mensaje": mensaje}
