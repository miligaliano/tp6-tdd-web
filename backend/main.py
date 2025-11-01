# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- MODELO ----
class Compra(BaseModel):
    email: str
    fecha_visita: str
    cantidad: int
    edades: List[int]
    tipo_pase: List[str]
    forma_pago: str

# ---- FUNCIONES ----
def obtener_descuento_por_edad(edad):
    if edad < 3:
        return 1.0  # 100% de descuento
    elif edad < 15:
        return 0.5  # 50% de descuento
    elif edad < 60:
        return 0.0  # sin descuento
    elif edad <= 110:
        return 0.5  # 50% de descuento
    else:
        raise ValueError("Edad fuera de rango")

def obtener_precio_base(tipo_pase):
    precios = {
        "regular": 5000,
        "VIP": 10000
    }
    return precios.get(tipo_pase.lower(), 0)

# ---- ENDPOINT PRINCIPAL ----
@app.post("/comprar")
def comprar(compra: Compra):
    if len(compra.edades) != compra.cantidad or len(compra.tipo_pase) != compra.cantidad:
        raise HTTPException(status_code=400, detail="Los datos de visitantes no coinciden con la cantidad ingresada.")

    total = 0
    detalle = []

    for edad, tipo_pase in zip(compra.edades, compra.tipo_pase):
        if edad < 0 or edad > 110:
            raise HTTPException(status_code=400, detail=f"Edad inválida: {edad}")

        precio_base = obtener_precio_base(tipo_pase)
        descuento = obtener_descuento_por_edad(edad)
        precio_final = precio_base * (1 - descuento)
        total += precio_final

        detalle.append(f"{tipo_pase.title()} - Edad {edad}: ${precio_final:.2f}")

    mensaje = (
        f"Compra registrada correctamente.<br><br>"
        f"Fecha de visita: {compra.fecha_visita}<br>"
        f"Forma de pago: {compra.forma_pago}<br>"
        f"Entradas: {compra.cantidad}<br><br>"
        f"Detalle:<br>" + "<br>".join(detalle) +
        f"<br><br>💰 Total a pagar: ${total:.2f}"
    )

    if compra.forma_pago.strip().lower() == "tarjeta":
        mensaje += "<br><br> Redirigiendo a Mercado Pago..."
    else:
        mensaje += "<br><br> Pago en boletería."

    return {"mensaje": mensaje}


# ---- ENDPOINT DE EMAIL ----
@app.post("/enviar-confirmacion")
def enviar_confirmacion(data: dict):
    try:
        remitente = "tu_correo@ejemplo.com"
        destinatario = data.get("email")
        mensaje = data.get("mensaje")

        msg = MIMEMultipart()
        msg["From"] = remitente
        msg["To"] = destinatario
        msg["Subject"] = "Confirmación de compra - Parque Aventura"
        msg.attach(MIMEText(mensaje, "plain"))

        # Aquí se puede usar un servidor SMTP real, por ejemplo Gmail
        # smtp = smtplib.SMTP("smtp.gmail.com", 587)
        # smtp.starttls()
        # smtp.login(remitente, "tu_contraseña")
        # smtp.sendmail(remitente, destinatario, msg.as_string())
        # smtp.quit()

        print("Correo simulado enviado a:", destinatario)
        print("Mensaje:\n", mensaje)

        return {"ok": True, "mensaje": "Correo enviado correctamente (simulado)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
