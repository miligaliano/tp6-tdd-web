# 🎡 Parque Aventura - Sistema de Compra de Entradas (ISW - 2025)

Este proyecto es una aplicación web para la gestión de compra de entradas del parque EcoHarmony. Incluye un backend en Python con FastAPI, un frontend web personalizado con HTML/CSS/JS, y una base de datos SQLite para usuarios registrados.

---

## 📋 Pruebas Implementadas

La siguiente tabla resume todos los casos de prueba desarrollados para validar la lógica de negocio, cubriendo tanto los escenarios del enunciado como los casos límite inferidos.

| Tipo de Prueba                       | Descripción                                    | Fuente       |
| :----------------------------------- | :--------------------------------------------- | :----------- |
| `test_compra_exitosa_tarjeta`        | Compra válida con tarjeta (Mercado Pago)       | Enunciado    |
| `test_compra_sin_forma_pago`         | Falla si no se selecciona forma de pago        | Enunciado    |
| `test_compra_fecha_cerrado`          | Falla si el parque está cerrado (Domingo)      | Enunciado    |
| `test_compra_mas_de_10_entradas`     | Falla si se piden más de 10 entradas           | Enunciado    |
| `test_compra_usuario_no_registrado`  | Solo usuarios registrados pueden comprar       | **Inferida** |
| `test_compra_sin_edades`             | Se deben indicar las edades de los visitantes  | **Inferida** |
| `test_compra_pago_efectivo`          | El pago en boletería es un método válido       | **Inferida** |
| `test_compra_tipo_vip`               | El cálculo para el pase VIP es correcto        | **Inferida** |
| `test_compra_fecha_futura_valida`    | Se pueden comprar entradas para fechas futuras | **Inferida** |
| `test_compra_fecha_hoy_es_valida`    | Se puede comprar para el día actual            | **Inferida** |
| `test_compra_fecha_pasada_falla`     | No se puede comprar para una fecha pasada      | **Inferida** |
| `test_compra_cantidad_limite_valida` | Se puede comprar 1 y 10 entradas (límites)     | **Inferida** |
| `test_compra_cantidad_cero_falla`    | No se pueden comprar 0 entradas                | **Inferida** |

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos en orden para configurar y ejecutar el proyecto en tu máquina local.

### Paso 1: Requisitos Previos

Asegúrate de tener **Python 3** instalado. Luego, abre una terminal en la carpeta raíz del proyecto e instala las librerías necesarias:

```bash
pip install pytest
pip install customtkinter
```

### Paso 2: Crear e Inicializar la Base de Datos (Ejecuta en la consola el siguiente comando)

python backend/db/setup_database.py

### Paso 3: Ejecutar la Suite de Pruebas (Ejecuta en la consola el siguiente comando)

python run_tests.py

### Paso 4: Instalar dependencias (Ejecuta en la consola el siguiente comando)

pip install -r requirements.txt

### Paso 5: Iniciar el backend (Ejecuta en la consola el siguiente comando)

python -m uvicorn backend.main:app --reload

### Paso 6: Iniciar el frontend (Ejecuta en la consola el siguiente comando)

cd frontend
python -m http.server 8080

