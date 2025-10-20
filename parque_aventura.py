import re
from datetime import date
from database import buscar_usuario_por_email, obtener_conexion, crear_tabla_usuarios
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


## ------------------------------------------------------------------------
## CLASES DE UI INTEGRADAS
## ------------------------------------------------------------------------


class VentanaPagoTarjeta(ctk.CTkToplevel):
    """Ventana modal para el pago con tarjeta y envío de recibo por email.

    Al procesar: valida campos de tarjeta, valida/crea email en BD y
    envía (o simula) el correo sólo si el email ingresado coincide con
    el usuario registrado o se registró correctamente.
    """
    def __init__(self, master, compra_original: Compra, ui_principal: 'ComprarEntradasUI'):
        super().__init__(master)
        self.compra_original = compra_original
        self.ui_principal = ui_principal
        self.today = date.today()

        self.title("💳 Procesar Pago con Tarjeta")
        self.geometry("600x600")
        self.transient(master)

        ctk.CTkLabel(self, text="Pasarela de Pago mercado pago", font=("Arial", 16)).pack(pady=20)

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="Email para el recibo:").pack(anchor="w", padx=15, pady=(10, 5))
        self.email_var = ctk.StringVar(value=self.compra_original.usuario.email)
        self.entry_email = ctk.CTkEntry(form_frame, textvariable=self.email_var, width=350)
        self.entry_email.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Nombre y Apellido (como figura en la tarjeta):").pack(anchor="w", padx=15, pady=(10, 5))
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre Apellido", width=350)
        self.entry_nombre.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Número de Tarjeta:").pack(anchor="w", padx=15, pady=(10, 5))
        self.entry_tarjeta = ctk.CTkEntry(form_frame, placeholder_text="16 dígitos (sin espacios)", width=350)
        self.entry_tarjeta.pack(anchor="w", padx=15, pady=(0, 10))

        secure_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        secure_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(secure_frame, text="Vencimiento:").grid(row=0, column=0, sticky="w")
        self.entry_mes = ctk.CTkEntry(secure_frame, placeholder_text="MM", width=60)
        self.entry_mes.grid(row=1, column=0, padx=(0, 10))
        self.entry_anio = ctk.CTkEntry(secure_frame, placeholder_text="AAAA", width=70)
        self.entry_anio.grid(row=1, column=1)
        ctk.CTkLabel(secure_frame, text="CVV:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.entry_cvv = ctk.CTkEntry(secure_frame, placeholder_text="CVV", width=70, show="*")
        self.entry_cvv.grid(row=1, column=2, padx=(20, 0))

        self.label_error_pago = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 12))
        self.label_error_pago.pack(pady=(10, 0))

        precio_total = self.compra_original.calcular_monto_total()
        self.btn_pagar = ctk.CTkButton(self, text=f"Pagar ${precio_total}", command=self._procesar_pago, height=40)
        self.btn_pagar.pack(pady=20, padx=20)

        self.grab_set()

    def _validar_campos(self) -> (bool, str):
        try:
            nombre = self.entry_nombre.get()
            if not nombre or len(nombre) < 3:
                return False, "Por favor, ingrese su nombre y apellido."

            tarjeta = self.entry_tarjeta.get()
            if not tarjeta.isdigit() or len(tarjeta) != 16:
                return False, "El número de tarjeta debe tener 16 dígitos numéricos."

            mes_str = self.entry_mes.get()
            if not mes_str.isdigit():
                return False, "El mes debe ser un número."
            mes = int(mes_str)
            if not (1 <= mes <= 12):
                return False, "El mes de vencimiento debe estar entre 1 y 12."

            anio_str = self.entry_anio.get()
            if not anio_str.isdigit() or len(anio_str) != 4:
                return False, "El año debe tener 4 dígitos (ej: 2025)."
            anio = int(anio_str)
            if anio < self.today.year or (anio == self.today.year and mes < self.today.month):
                return False, "La tarjeta de crédito está vencida."

            cvv = self.entry_cvv.get()
            if not cvv.isdigit() or len(cvv) != 3:
                return False, "El CVV debe tener 3 dígitos numéricos."

        except ValueError:
            return False, "Por favor, revise que los campos numéricos sean correctos."
        return True, ""

    def _enviar_correo_confirmacion(self, cuerpo_mensaje, destinatario_email):
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

    def _procesar_pago(self):
        es_valido, mensaje_error = self._validar_campos()
        if not es_valido:
            self.label_error_pago.configure(text=f"⚠️ {mensaje_error}")
            return

        self.label_error_pago.configure(text="")
        entered_email = self.email_var.get().strip()

        # procesar compra
        resultado = self.compra_original.procesar()
        self.ui_principal.text_resultado.delete("1.0", "end")

        if not resultado.get("ok"):
            self.ui_principal.text_resultado.insert("end", resultado.get("mensaje"))
            self.destroy()
            return

        # Verificar/registrar email en la BD
        try:
            crear_tabla_usuarios()
            db_row = buscar_usuario_por_email(self.compra_original.usuario.email)

            if self.compra_original.usuario.registrado and db_row is not None:
                # Usuario registrado: el email ingresado debe coincidir
                if entered_email != self.compra_original.usuario.email:
                    mensaje_final = (
                        f"❌ El email ingresado ({entered_email}) no coincide con el usuario registrado ({self.compra_original.usuario.email}).\n"
                        f"No se puede enviar el recibo."
                    )
                    self.ui_principal.text_resultado.insert("end", mensaje_final)
                    self.destroy()
                    return
            else:
                # Insertar nuevo usuario (registro automático)
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT OR IGNORE INTO usuarios (email, nombre, password_hash) VALUES (?, ?, ?)",
                        (entered_email, "RegistroAutomático", ""),
                    )
                    conn.commit()
                self.compra_original.usuario.email = entered_email
                self.compra_original.usuario.registrado = True

            # Intentar enviar correo (o simular)
            try:
                enviado = self._enviar_correo_confirmacion(resultado["mensaje"], entered_email)
                if enviado:
                    mensaje_final = (
                        f"✅ ¡Pago con tarjeta procesado con éxito!\n\n{resultado['mensaje']}\n\n📧 Se envió un recibo a {entered_email}."
                    )
                else:
                    mensaje_final = (
                        f"✅ ¡Pago con tarjeta procesado con éxito!\n\n{resultado['mensaje']}\n\n⚠️ No se pudo enviar el email de confirmación a {entered_email}."
                    )
            except Exception as e:
                mensaje_final = f"✅ Pago procesado, pero fallo el envío del email: {e}"

        except Exception as e:
            mensaje_final = f"❌ Error al verificar/registrar email: {e}"

        self.ui_principal.text_resultado.insert("end", mensaje_final)
        self.destroy()



class ComprarEntradasUI(ctk.CTk):
    def __init__(self, usuario_logueado: Usuario):
        super().__init__()
        self.usuario_logueado = usuario_logueado

        self.title("🎟️ Compra de Entradas - EcoHarmony Park")
        self.geometry("600x600")

        ctk.CTkLabel(self, text=f"Bienvenido, {self.usuario_logueado.email}", font=("Arial", 16)).pack(pady=10)

        ctk.CTkLabel(self, text="Seleccione la fecha de visita:").pack(pady=(10, 5))
        self.fecha_frame = ctk.CTkFrame(self)
        self.fecha_frame.pack()
        today = date.today()
        self.anio_var = ctk.StringVar(value=str(today.year))
        self.mes_var = ctk.StringVar(value=str(today.month))
        self.dia_var = ctk.StringVar(value=str(today.day))
        self.om_anio = ctk.CTkOptionMenu(self.fecha_frame, variable=self.anio_var, values=[str(today.year), str(today.year + 1)], command=self.actualizar_dias)
        self.om_mes = ctk.CTkOptionMenu(self.fecha_frame, variable=self.mes_var, values=[str(m) for m in range(1, 13)], command=self.actualizar_dias)
        self.om_dia = ctk.CTkOptionMenu(self.fecha_frame, variable=self.dia_var, command=self.actualizar_dias)
        self.om_anio.grid(row=0, column=0, padx=5, pady=5)
        self.om_mes.grid(row=0, column=1, padx=5, pady=5)
        self.om_dia.grid(row=0, column=2, padx=5, pady=5)
        self.label_feedback_fecha = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.label_feedback_fecha.pack(pady=(5, 10))

        ctk.CTkLabel(self, text="Cantidad de entradas:").pack(pady=(15, 5))
        self.cantidad_frame = ctk.CTkFrame(self)
        self.cantidad_frame.pack()
        self.cantidad_var = ctk.StringVar(value="2")
        self.btn_menos = ctk.CTkButton(self.cantidad_frame, text="-", width=40, command=lambda: self.ajustar_cantidad(-1))
        self.btn_menos.grid(row=0, column=0, padx=(0, 5))
        self.entry_cantidad = ctk.CTkEntry(self.cantidad_frame, textvariable=self.cantidad_var, width=60, justify="center")
        self.entry_cantidad.grid(row=0, column=1)
        self.btn_mas = ctk.CTkButton(self.cantidad_frame, text="+", width=40, command=lambda: self.ajustar_cantidad(1))
        self.btn_mas.grid(row=0, column=2, padx=(5, 0))

        ctk.CTkLabel(self, text="Tipo de pase:").pack(pady=(15, 5))
        self.tipo_pase = ctk.CTkOptionMenu(self, values=["regular", "VIP"]) 
        self.tipo_pase.set("regular")
        self.tipo_pase.pack()

        ctk.CTkLabel(self, text="Forma de pago:").pack(pady=5)
        self.forma_pago = ctk.CTkOptionMenu(self, values=["efectivo", "tarjeta"]) 
        self.forma_pago.set("efectivo")
        self.forma_pago.pack()

        self.btn_comprar = ctk.CTkButton(self, text="Comprar entradas", command=self.realizar_compra)
        self.btn_comprar.pack(pady=20)

        self.text_resultado = ctk.CTkTextbox(self, width=500, height=120)
        self.text_resultado.pack(pady=10)

        self.actualizar_dias()

    def ajustar_cantidad(self, cambio):
        try:
            cantidad_actual = int(self.cantidad_var.get())
            nueva_cantidad = cantidad_actual + cambio
            min_entradas = ConfiguracionParque.CANTIDAD_MIN_ENTRADAS
            max_entradas = ConfiguracionParque.CANTIDAD_MAX_ENTRADAS
            if min_entradas <= nueva_cantidad <= max_entradas:
                self.cantidad_var.set(str(nueva_cantidad))
        except ValueError:
            self.cantidad_var.set(str(ConfiguracionParque.CANTIDAD_MIN_ENTRADAS))

    def actualizar_dias(self, *args):
        try:
            year = int(self.anio_var.get())
            month = int(self.mes_var.get())
            _, num_dias = monthrange(year, month)
            dias_disponibles = [str(d) for d in range(1, num_dias + 1)]
            self.om_dia.configure(values=dias_disponibles)
            current_dia = self.dia_var.get()
            if not current_dia.isdigit() or int(current_dia) > num_dias:
                self.dia_var.set(str(num_dias))
            elif int(current_dia) < 1:
                self.dia_var.set("1")
            fecha_seleccionada = date(year, month, int(self.dia_var.get()))
            self.btn_comprar.configure(state="normal")
            if fecha_seleccionada < date.today():
                self.label_feedback_fecha.configure(text="⚠️ La fecha no puede ser anterior a hoy.", text_color="red")
                self.btn_comprar.configure(state="disabled")
            elif fecha_seleccionada.weekday() not in ConfiguracionParque.DIAS_ABIERTOS:
                self.label_feedback_fecha.configure(text="🚫 El parque está cerrado ese día.", text_color="orange")
                self.btn_comprar.configure(state="disabled")
            else:
                self.label_feedback_fecha.configure(text="✅ Fecha de visita válida.", text_color="green")
        except (ValueError, TypeError):
            self.label_feedback_fecha.configure(text="")
            self.btn_comprar.configure(state="disabled")

    def realizar_compra(self):
        try:
            fecha_visita = date(int(self.anio_var.get()), int(self.mes_var.get()), int(self.dia_var.get()))
            cantidad = int(self.cantidad_var.get())
        except ValueError:
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert("end", "⚠️ Datos inválidos. Por favor, revise su selección.")
            return

        edades = [25] * cantidad
        tipo = self.tipo_pase.get()
        forma = self.forma_pago.get()

        compra = Compra(self.usuario_logueado, fecha_visita, cantidad, edades, tipo, forma)

        if forma == "tarjeta":
            VentanaPagoTarjeta(master=self, compra_original=compra, ui_principal=self)
        else:
            resultado = compra.procesar()
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert("end", resultado.get("mensaje"))
