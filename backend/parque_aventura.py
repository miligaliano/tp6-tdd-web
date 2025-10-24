import re
from datetime import date
from .db.database import buscar_usuario_por_email, obtener_conexion, crear_tabla_usuarios
import customtkinter as ctk
from calendar import monthrange

# --- EMAIL / ENV ---
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Cargar .env y configurar UI
load_dotenv()
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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
            return

        if any(e <= 0 for e in self.edades):
            self.errores.append("Edad inválida: todas deben ser mayores a 0.")

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
        mensaje = (f"🎟️ Compra confirmada\n" f"- Usuario: {self.usuario.email}\n"f"- Cantidad de entradas: {self.cantidad}\n"f"- Fecha de visita: {self.fecha_visita.strftime('%d/%m/%Y')}\n"f"- Precio total: ${total}\n"f"- Forma de pago: {self.forma_pago.capitalize()}\n")
        
        if self.forma_pago == "tarjeta":
            mensaje += " Redirigiendo a Mercado Pago..."
        else:
            mensaje += " Pago en boletería."

        return {"ok": True, "mensaje": mensaje}


## ------------------------------------------------------------------------
## CLASES DE UI INTEGRADAS
## ------------------------------------------------------------------------

def enviar_correo_confirmacion(cuerpo_mensaje, destinatario_email):
    import os
    import ssl
    import smtplib
    from email.message import EmailMessage

    EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
    PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")
    SIMULATE_EMAIL = os.environ.get("SIMULATE_EMAIL", "1")

    msg = EmailMessage()
    msg['Subject'] = "Confirmación de Compra - EcoHarmony Park"
    msg['From'] = EMAIL_EMISOR if EMAIL_EMISOR else "simulado@local"
    msg['To'] = destinatario_email
    msg.set_content(f"¡Gracias por tu compra!\n\nAquí está el resumen:\n\n{cuerpo_mensaje}")

    if not EMAIL_EMISOR or not PASSWORD_EMISOR:
        if SIMULATE_EMAIL == "1":
            print(f"Simulación: correo enviado a {destinatario_email} (credenciales no configuradas).")
            return True
        else:
            raise ValueError("Credenciales de email no encontradas.")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_EMISOR, PASSWORD_EMISOR)
        smtp.send_message(msg)
    return True


