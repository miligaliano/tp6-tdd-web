import customtkinter as ctk
from datetime import date, timedelta
from comprar_entradas import procesar_compra, validar_email


# Configuración inicial
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ComprarEntradasUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎟️ Compra de Entradas - Parque Aventura")
        self.geometry("600x600")

        # --- Datos del usuario ---
        ctk.CTkLabel(self, text="Mail del usuario:").pack(pady=5)
        self.entry_mail = ctk.CTkEntry(self, width=250)
        self.entry_mail.pack()

        ctk.CTkLabel(self, text="Contraseña:").pack(pady=5)
        self.entry_pass = ctk.CTkEntry(self, width=250, show="*")
        self.entry_pass.pack()

        # --- Fecha de visita ---
        ctk.CTkLabel(
            self, text="Fecha de visita (días a futuro):").pack(pady=5)
        self.spin_dias = ctk.CTkSlider(
            self, from_=0, to=30, number_of_steps=30)
        self.spin_dias.set(1)
        self.spin_dias.pack()

        # --- Cantidad de entradas ---
        ctk.CTkLabel(self, text="Cantidad de entradas (1–10):").pack(pady=5)
        self.spin_cantidad = ctk.CTkSlider(
            self, from_=1, to=10, number_of_steps=9)
        self.spin_cantidad.set(2)
        self.spin_cantidad.pack()

        # --- Tipo de pase ---
        ctk.CTkLabel(self, text="Tipo de pase:").pack(pady=5)
        self.tipo_pase = ctk.CTkOptionMenu(self, values=["regular", "VIP"])
        self.tipo_pase.set("regular")
        self.tipo_pase.pack()

        # --- Forma de pago ---
        ctk.CTkLabel(self, text="Forma de pago:").pack(pady=5)
        self.forma_pago = ctk.CTkOptionMenu(
            self, values=["efectivo", "tarjeta"])
        self.forma_pago.set("efectivo")
        self.forma_pago.pack()

        # --- Botón comprar ---
        self.btn_comprar = ctk.CTkButton(
            self, text="Comprar entradas", command=self.realizar_compra)
        self.btn_comprar.pack(pady=15)

        # --- Resultado ---
        self.text_resultado = ctk.CTkTextbox(self, width=500, height=200)
        self.text_resultado.pack(pady=10)

    def realizar_compra(self):
        """Llama al módulo principal y muestra el resultado."""
        usuario = {
            "email": self.entry_mail.get(),
            "registrado": bool(self.entry_mail.get() and self.entry_pass.get())
        }
        dias_futuro = int(self.spin_dias.get())
        cantidad = int(self.spin_cantidad.get())
        fecha_visita = date.today() + timedelta(days=dias_futuro)
        edades = [25] * cantidad  # ejemplo automático
        tipo = self.tipo_pase.get()
        forma = self.forma_pago.get()

        resultado = procesar_compra(
            usuario, fecha_visita, cantidad, edades, tipo, forma)
        self.text_resultado.delete("1.0", "end")
        self.text_resultado.insert("end", resultado["mensaje"])

        if not validar_email(self.entry_mail.get()):
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert(
                "end", "⚠️ El email ingresado no es válido.")
        return


if __name__ == "__main__":
    app = ComprarEntradasUI()
    app.mainloop()
