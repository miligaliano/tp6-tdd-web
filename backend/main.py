# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

from backend.parque_aventura import Usuario, Compra
from backend.db.database import crear_tabla_usuarios
from backend.parque_aventura import enviar_correo_confirmacion  # si lo separaste


app = FastAPI(title="EcoHarmony Park API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar BD al arrancar
crear_tabla_usuarios()

class CompraRequest(BaseModel):
    email: EmailStr
    fecha_visita: date
    cantidad: int
    edades: list[int]
    tipo_pase: str
    forma_pago: str

@app.post("/comprar")
def procesar_compra(data: CompraRequest):
    usuario = Usuario.desde_la_sesion(data.email)
    compra = Compra(usuario, data.fecha_visita, data.cantidad, data.edades, data.tipo_pase, data.forma_pago)
    resultado = compra.procesar()

    if not resultado["ok"]:
        raise HTTPException(status_code=400, detail=resultado["mensaje"])
    return resultado

class EmailRequest(BaseModel):
    email: EmailStr
    mensaje: str

@app.post("/enviar-confirmacion")
def enviar_email(data: EmailRequest):
    try:
        enviado = enviar_correo_confirmacion(data.mensaje, data.email)
        if enviado:
            return {"ok": True, "mensaje": f"Correo enviado a {data.email}"}
        else:
            raise HTTPException(status_code=500, detail="No se pudo enviar el correo.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))