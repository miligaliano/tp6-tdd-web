import customtkinter as ctk
from datetime import date
from calendar import monthrange

# --- NUEVOS IMPORTS PARA EL EMAIL ---
import smtplib
import ssl
from email.message import EmailMessage
import os                 # Para leer variables de entorno
from dotenv import load_dotenv  # Para cargar el archivo .env

# Cargar las variables del archivo .env al entorno
load_dotenv()
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Usuario:
    """Clase ficticia para simular el Usuario."""
    def __init__(self, email, registrado=True):
        self.email = email
        self.registrado = registrado

    @staticmethod
    def desde_la_sesion(email):
        """Simula que encuentra al usuario en la 'base de datos'."""
        if "@" in email:
            return Usuario(email, registrado=True)
        return Usuario(email, registrado=False)

class Compra:
    """Clase ficticia para simular la Compra."""
    def __init__(self, usuario, fecha_visita, cantidad, edades, tipo, forma):
        self.usuario = usuario
        self.fecha_visita = fecha_visita
        self.cantidad = cantidad
        self.edades = edades
        self.tipo_pase = tipo
        self.forma_pago = forma
        self.precio_total_simulado = 100 * cantidad # Simulación

    def procesar(self):
        """Simula el procesamiento de la compra."""
        mensaje = (
            f"--- Compra Exitosa ---\n"
            f"Usuario: {self.usuario.email}\n"
            f"Fecha: {self.fecha_visita}\n"
            f"Entradas: {self.cantidad} ({self.tipo_pase})\n"
            f"Método: {self.forma_pago}\n"
            f"Total: ${self.precio_total_simulado}"
        )
        return {"mensaje": mensaje, "exito": True}

class ConfiguracionParque:
    """Clase ficticia para simular la Configuración."""
    CANTIDAD_MIN_ENTRADAS = 1
    CANTIDAD_MAX_ENTRADAS = 10
    DIAS_ABIERTOS = [0, 1, 2, 3, 4, 5, 6] # Lunes=0, Domingo=6





class VentanaPagoTarjeta(ctk.CTkToplevel):
    """
    ventana modal para el pago con tarjeta.
 
    """
    def __init__(self, master, compra_original: Compra, ui_principal: 'ComprarEntradasUI'):
        super().__init__(master)
        self.compra_original = compra_original
        self.ui_principal = ui_principal # Referencia a la ventana principal
        
        # Guardamos la fecha actual para las validaciones
        self.today = date.today()

        self.title("💳 Procesar Pago con Tarjeta")
        self.geometry("600x600")

        self.transient(master)

        ctk.CTkLabel(self, text="Pasarela de Pago mercado pago", font=("Arial", 16)).pack(pady=20)

        # Frame para los datos
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        # --- CAMPO 1: Email ---
        ctk.CTkLabel(form_frame, text="Email para el recibo:").pack(anchor="w", padx=15, pady=(10, 5))
        self.email_var = ctk.StringVar(value=self.compra_original.usuario.email)
        self.entry_email = ctk.CTkEntry(form_frame, textvariable=self.email_var, width=350)
        self.entry_email.pack(anchor="w", padx=15, pady=(0, 10))

        # --- CAMPO 2: Nombre y Apellido (NUEVO) ---
        ctk.CTkLabel(form_frame, text="Nombre y Apellido (como figura en la tarjeta):").pack(anchor="w", padx=15, pady=(10, 5))
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre Apellido", width=350)
        self.entry_nombre.pack(anchor="w", padx=15, pady=(0, 10))
        
        # --- CAMPO 3: Número de Tarjeta (MODIFICADO) ---
        ctk.CTkLabel(form_frame, text="Número de Tarjeta:").pack(anchor="w", padx=15, pady=(10, 5))
        self.entry_tarjeta = ctk.CTkEntry(form_frame, placeholder_text="16 dígitos (sin espacios)", width=350)
        self.entry_tarjeta.pack(anchor="w", padx=15, pady=(0, 10))

        # --- CAMPO 4 y 5: Vencimiento y CVV (MODIFICADO) ---
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

        # --- Label para mostrar errores de validación ---
        self.label_error_pago = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 12))
        self.label_error_pago.pack(pady=(10, 0))

        # --- Botón de Pagar ---
        self.btn_pagar = ctk.CTkButton(self, text=f"Pagar ${self.compra_original.precio_total_simulado}",
                                       command=self._procesar_pago, height=40)
        self.btn_pagar.pack(pady=20, padx=20)

        # CORRECCIÓN: grab_set() al final
        self.grab_set()

    def _validar_campos(self) -> (bool, str): # type: ignore
        """
        Valida todos los campos del formulario antes de procesar el pago.
        Retorna (True, "") si es válido, o (False, "mensaje de error") si no.
        """
        try:
            # 1. Validar Nombre
            nombre = self.entry_nombre.get()
            if not nombre or len(nombre) < 3:
                return False, "Por favor, ingrese su nombre y apellido."

            # 2. Validar Tarjeta
            tarjeta = self.entry_tarjeta.get()
            if not tarjeta.isdigit() or len(tarjeta) != 16:
                return False, "El número de tarjeta debe tener 16 dígitos numéricos."
            
            # 3. Validar Mes
            mes_str = self.entry_mes.get()
            if not mes_str.isdigit():
                 return False, "El mes debe ser un número."
            mes = int(mes_str)
            if not (1 <= mes <= 12):
                return False, "El mes de vencimiento debe estar entre 1 y 12."
            
            # 4. Validar Año
            anio_str = self.entry_anio.get()
            if not anio_str.isdigit() or len(anio_str) != 4:
                 return False, "El año debe tener 4 dígitos (ej: 2025)."
            anio = int(anio_str)
            
            current_year = self.today.year
            current_month = self.today.month

            if anio < current_year:
                return False, "El año de la tarjeta no puede ser un año pasado."
            
            # 5. Validar si la tarjeta ya expiró (mismo año, mes anterior)
            if anio == current_year and mes < current_month:
                return False, "La tarjeta de crédito está vencida."

            # 6. Validar CVV
            cvv = self.entry_cvv.get()
            if not cvv.isdigit() or len(cvv) != 3:
                return False, "El CVV debe tener 3 dígitos numéricos."

        except ValueError:
            return False, "Por favor, revise que los campos numéricos sean correctos."
        
        # Si todo está bien
        return True, ""


    def _enviar_correo_confirmacion(self, cuerpo_mensaje, destinatario_email):
        """
        Envía un correo de confirmación usando un servidor SMTP de GMAIL.
        """
        
        EMAIL_EMISOR = os.environ.get("EMAIL_EMISOR")
        PASSWORD_EMISOR = os.environ.get("PASSWORD_EMISOR")

        if not EMAIL_EMISOR or not PASSWORD_EMISOR:
            print("Error: Credenciales de email no encontradas en .env")
            raise ValueError("Credenciales de email no encontradas.")

        msg = EmailMessage()
        msg['Subject'] = "Confirmación de Compra - EcoHarmony Park"
        msg['From'] = EMAIL_EMISOR
        msg['To'] = destinatario_email
        msg.set_content(f"¡Gracias por tu compra!\n\nAquí está el resumen:\n\n{cuerpo_mensaje}")

        context = ssl.create_default_context()
        
        print(f"Intentando enviar email a {destinatario_email} desde {EMAIL_EMISOR}...")

        try:
            # --- CÓDIGO PARA GMAIL ---
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(EMAIL_EMISOR, PASSWORD_EMISOR)
                smtp.send_message(msg)
            print("Email enviado exitosamente.")
        except Exception as e:
            print(f"Error al enviar email: {e}")
            raise e


    def _procesar_pago(self):
        """
        Valida los campos y, si son correctos, procesa la compra,
        envía el email y cierra la ventana.
        """
        
        # --- PASO 1: VALIDAR LOS CAMPOS ---
        es_valido, mensaje_error = self._validar_campos()
        
        if not es_valido:
            self.label_error_pago.configure(text=f"⚠️ {mensaje_error}")
            return # Detiene la ejecución si hay un error
        
        # Si es válido, limpia el error y continúa
        self.label_error_pago.configure(text="")

        # --- PASO 2: PROCESAR LA COMPRA (como antes) ---
        self.compra_original.usuario.email = self.email_var.get()
        resultado = self.compra_original.procesar()

        # --- PASO 3: ACTUALIZAR UI PRINCIPAL Y ENVIAR EMAIL ---
        self.ui_principal.text_resultado.delete("1.0", "end")
        
        destinatario = self.email_var.get()
        mensaje_final = ""
        
        if resultado["exito"]:
            try:
                # 3. Intentar enviar el correo
                self._enviar_correo_confirmacion(resultado["mensaje"], destinatario)
                mensaje_final = (
                    f"✅ ¡Pago con tarjeta procesado con éxito!\n\n"
                    f"{resultado['mensaje']}\n\n"
                    f"📧 Se envió un recibo a {destinatario}."
                )
            except Exception as e:
                mensaje_final = (
                    f"✅ ¡Pago con tarjeta procesado con éxito!\n\n"
                    f"{resultado['mensaje']}\n\n"
                    f"⚠️ No se pudo enviar el email de confirmación a {destinatario}.\n"
                    f"Error: {e}"
                )
        else:
            mensaje_final = f"❌ Error en el pago: {resultado['mensaje']}"

        self.ui_principal.text_resultado.insert("end", mensaje_final)

        # --- PASO 4: CERRAR LA VENTANA MODAL ---
        self.destroy()


class ComprarEntradasUI(ctk.CTk):
    def __init__(self, usuario_logueado: Usuario):
        super().__init__()
        self.usuario_logueado = usuario_logueado

        self.title("🎟️ Compra de Entradas - EcoHarmony Park")
        self.geometry("600x600")

        ctk.CTkLabel(self, text=f"Bienvenido, {self.usuario_logueado.email}", font=(
            "Arial", 16)).pack(pady=10)

        ctk.CTkLabel(self, text="Seleccione la fecha de visita:").pack(
            pady=(10, 5))
        self.fecha_frame = ctk.CTkFrame(self)
        self.fecha_frame.pack()
        today = date.today()
        self.anio_var = ctk.StringVar(value=str(today.year))
        self.mes_var = ctk.StringVar(value=str(today.month))
        self.dia_var = ctk.StringVar(value=str(today.day))
        self.om_anio = ctk.CTkOptionMenu(self.fecha_frame, variable=self.anio_var, values=[
                                         str(today.year), str(today.year + 1)], command=self.actualizar_dias)
        self.om_mes = ctk.CTkOptionMenu(self.fecha_frame, variable=self.mes_var, values=[
                                        str(m) for m in range(1, 13)], command=self.actualizar_dias)
        self.om_dia = ctk.CTkOptionMenu(
            self.fecha_frame, variable=self.dia_var, command=self.actualizar_dias)
        self.om_anio.grid(row=0, column=0, padx=5, pady=5)
        self.om_mes.grid(row=0, column=1, padx=5, pady=5)
        self.om_dia.grid(row=0, column=2, padx=5, pady=5)
        self.label_feedback_fecha = ctk.CTkLabel(
            self, text="", font=("Arial", 12))
        self.label_feedback_fecha.pack(pady=(5, 10))

        ctk.CTkLabel(self, text="Cantidad de entradas:").pack(pady=(15, 5))
        self.cantidad_frame = ctk.CTkFrame(self)
        self.cantidad_frame.pack()

        self.cantidad_var = ctk.StringVar(value="2")

        self.btn_menos = ctk.CTkButton(
            self.cantidad_frame, text="-", width=40, command=lambda: self.ajustar_cantidad(-1))
        self.btn_menos.grid(row=0, column=0, padx=(0, 5))

        self.entry_cantidad = ctk.CTkEntry(
            self.cantidad_frame, textvariable=self.cantidad_var, width=60, justify="center")
        self.entry_cantidad.grid(row=0, column=1)

        self.btn_mas = ctk.CTkButton(
            self.cantidad_frame, text="+", width=40, command=lambda: self.ajustar_cantidad(1))
        self.btn_mas.grid(row=0, column=2, padx=(5, 0))

        ctk.CTkLabel(self, text="Tipo de pase:").pack(pady=(15, 5))
        self.tipo_pase = ctk.CTkOptionMenu(self, values=["regular", "VIP"])
        self.tipo_pase.set("regular")
        self.tipo_pase.pack()

        ctk.CTkLabel(self, text="Forma de pago:").pack(pady=5)
        self.forma_pago = ctk.CTkOptionMenu(
            self, values=["efectivo", "tarjeta"])
        self.forma_pago.set("efectivo")
        self.forma_pago.pack()

        self.btn_comprar = ctk.CTkButton(
            self, text="Comprar entradas", command=self.realizar_compra)
        self.btn_comprar.pack(pady=20)

        self.text_resultado = ctk.CTkTextbox(self, width=500, height=120)
        self.text_resultado.pack(pady=10)

        self.actualizar_dias()

    def ajustar_cantidad(self, cambio):
        """Ajusta la cantidad de entradas, respetando los límites."""
        try:
            cantidad_actual = int(self.cantidad_var.get())
            nueva_cantidad = cantidad_actual + cambio

            min_entradas = ConfiguracionParque.CANTIDAD_MIN_ENTRADAS
            max_entradas = ConfiguracionParque.CANTIDAD_MAX_ENTRADAS

            if min_entradas <= nueva_cantidad <= max_entradas:
                self.cantidad_var.set(str(nueva_cantidad))
        except ValueError:
            self.cantidad_var.set(
                str(ConfiguracionParque.CANTIDAD_MIN_ENTRADAS))

    def actualizar_dias(self, *args):
        """Actualiza el menú de días y proporciona feedback visual sobre la fecha."""
        try:
            year = int(self.anio_var.get())
            month = int(self.mes_var.get())

            _, num_dias = monthrange(year, month)
            dias_disponibles = [str(d) for d in range(1, num_dias + 1)]
            self.om_dia.configure(values=dias_disponibles)

            # Asegurarse de que el día seleccionado sea válido
            current_dia = self.dia_var.get()
            if not current_dia.isdigit() or int(current_dia) > num_dias:
                self.dia_var.set(str(num_dias))
            elif int(current_dia) < 1:
                 self.dia_var.set("1")

            fecha_seleccionada = date(year, month, int(self.dia_var.get()))
            self.btn_comprar.configure(state="normal") # Habilitar por defecto

            if fecha_seleccionada < date.today():
                self.label_feedback_fecha.configure(
                    text="⚠️ La fecha no puede ser anterior a hoy.", text_color="red")
                self.btn_comprar.configure(state="disabled")
            elif fecha_seleccionada.weekday() not in ConfiguracionParque.DIAS_ABIERTOS:
                self.label_feedback_fecha.configure(
                    text="🚫 El parque está cerrado ese día.", text_color="orange")
                self.btn_comprar.configure(state="disabled")
            else:
                self.label_feedback_fecha.configure(
                    text="✅ Fecha de visita válida.", text_color="green")

        except (ValueError, TypeError):
            self.label_feedback_fecha.configure(text="")
            self.btn_comprar.configure(state="disabled")

    def realizar_compra(self):
        """
        Obtiene los datos de la UI, crea el objeto Compra y decide
        cómo procesar el pago (directo o abriendo la ventana modal).
        """
        try:
            fecha_visita = date(
                int(self.anio_var.get()),
                int(self.mes_var.get()),
                int(self.dia_var.get())
            )
            cantidad = int(self.cantidad_var.get())
        except ValueError:
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert(
                "end", "⚠️ Datos inválidos. Por favor, revise su selección.")
            return

        edades = [25] * cantidad
        tipo = self.tipo_pase.get()
        forma = self.forma_pago.get()

        compra = Compra(self.usuario_logueado, fecha_visita,
                        cantidad, edades, tipo, forma)

        if forma == "tarjeta":
            VentanaPagoTarjeta(master=self, 
                               compra_original=compra, 
                               ui_principal=self)
        
        else:
            # Si es efectivo, procesar como antes
            resultado = compra.procesar()
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert("end", resultado["mensaje"])

if __name__ == "__main__":
    email_del_usuario_en_sesion = "usuario@registrado.com"
    usuario_actual = Usuario.desde_la_sesion(email_del_usuario_en_sesion)

    if not usuario_actual.registrado:
        print(
            f"Error: El usuario {email_del_usuario_en_sesion} no se encontró en la base de datos.")
    else:
        app = ComprarEntradasUI(usuario_logueado=usuario_actual)
        app.mainloop()