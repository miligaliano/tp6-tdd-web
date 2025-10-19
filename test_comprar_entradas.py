import pytest
from datetime import date, timedelta
from comprar_entradas import (
    validar_fecha_visita, validar_cantidad_entradas, validar_forma_pago,
    procesar_compra, calcular_monto_total, validar_email
)

# ------------------------------------------------------------------------
# VALIDACIONES UNITARIAS BÁSICAS
# ------------------------------------------------------------------------


def test_validar_email():
    """⚙️ INFERIDA: validar formato de email."""
    assert validar_email("usuario@example.com") is True
    assert validar_email("pepe123@mail.com") is True
    assert validar_email("sin_arroba.com") is False
    assert validar_email("mal@correo") is False
    assert validar_email("") is False
    print("✅ test_validar_email pasado")


def test_fecha_visita_valida():
    assert validar_fecha_visita(date.today()) is True
    assert validar_fecha_visita(date.today() + timedelta(days=5)) is True
    assert validar_fecha_visita(date.today() - timedelta(days=1)) is False
    print("✅ test_fecha_visita_valida pasado")


def test_cantidad_entradas_valida():
    assert validar_cantidad_entradas(1) is True
    assert validar_cantidad_entradas(10) is True
    assert validar_cantidad_entradas(11) is False
    assert validar_cantidad_entradas(0) is False
    print("✅ test_cantidad_entradas_valida pasado")


def test_forma_pago_valida():
    assert validar_forma_pago("efectivo") is True
    assert validar_forma_pago("tarjeta") is True
    assert validar_forma_pago("bitcoin") is False
    print("✅ test_forma_pago_valida pasado")


def test_calculo_monto_total():
    assert calcular_monto_total(2, "regular") == 20000
    assert calcular_monto_total(2, "VIP") == 30000
    print("✅ test_calculo_monto_total pasado")

# ------------------------------------------------------------------------
# PRUEBAS DE ACEPTACIÓN – SEGÚN ENUNCIADO OFICIAL
# ------------------------------------------------------------------------


def test_compra_exitosa_tarjeta():
    """✅ PRUEBA DEL ENUNCIADO: compra válida con pago por tarjeta (Mercado Pago)."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=1)
    resultado = procesar_compra(
        usuario, fecha, 2, [25, 30], "regular", "tarjeta")
    assert resultado["ok"] is True
    assert "Mercado Pago" in resultado["mensaje"]
    print("✅ test_compra_exitosa_tarjeta pasado")


def test_compra_sin_forma_pago():
    """✅ PRUEBA DEL ENUNCIADO: sin seleccionar forma de pago."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=2)
    resultado = procesar_compra(usuario, fecha, 2, [25, 30], "VIP", None)
    assert resultado["ok"] is False
    print("✅ test_compra_sin_forma_pago pasado")


def test_compra_fecha_cerrado():
    """✅ PRUEBA DEL ENUNCIADO: fecha de visita en día que el parque está cerrado (lunes)."""
    usuario = {"registrado": True}
    dias_hasta_lunes = (7 - date.today().weekday()) % 7  # próximo lunes
    fecha = date.today() + timedelta(days=dias_hasta_lunes)
    resultado = procesar_compra(
        usuario, fecha, 2, [25, 30], "regular", "efectivo")
    assert resultado["ok"] is False
    print("✅ test_compra_fecha_cerrado pasado")


def test_compra_mas_de_10_entradas():
    """✅ PRUEBA DEL ENUNCIADO: más de 10 entradas."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=3)
    resultado = procesar_compra(
        usuario, fecha, 11, [20]*11, "regular", "tarjeta")
    assert resultado["ok"] is False
    print("✅ test_compra_mas_de_10_entradas pasado")

# ------------------------------------------------------------------------
# PRUEBAS DE ACEPTACIÓN – INFERIDAS DE LOS CRITERIOS DE ACEPTACIÓN
# ------------------------------------------------------------------------


def test_compra_usuario_no_registrado():
    """⚙️ INFERIDA: solo usuarios registrados pueden comprar."""
    usuario = {"registrado": False}
    fecha = date.today() + timedelta(days=1)
    resultado = procesar_compra(
        usuario, fecha, 2, [25, 30], "regular", "efectivo")
    assert resultado["ok"] is False
    print("✅ test_compra_usuario_no_registrado pasado")


def test_compra_sin_edades():
    """⚙️ INFERIDA: se debe indicar la edad de cada visitante."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=1)
    resultado = procesar_compra(usuario, fecha, 3, [], "regular", "tarjeta")
    assert resultado["ok"] is False
    print("✅ test_compra_sin_edades pasado")


def test_compra_pago_efectivo():
    """⚙️ INFERIDA: pago en boletería con efectivo."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=2)
    resultado = procesar_compra(
        usuario, fecha, 2, [18, 22], "regular", "efectivo")
    assert resultado["ok"] is True
    assert "Pago en boletería" in resultado["mensaje"]
    print("✅ test_compra_pago_efectivo pasado")


def test_compra_tipo_vip():
    """⚙️ INFERIDA: compra con tipo de pase VIP."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=2)
    resultado = procesar_compra(usuario, fecha, 2, [18, 22], "VIP", "tarjeta")
    assert resultado["ok"] is True
    assert "Mercado Pago" in resultado["mensaje"]
    print("✅ test_compra_tipo_vip pasado")


def test_compra_fecha_futura_valida():
    """⚙️ INFERIDA: fecha futura válida dentro de días abiertos."""
    usuario = {"registrado": True}
    fecha = date.today() + timedelta(days=10)
    resultado = procesar_compra(usuario, fecha, 1, [30], "regular", "efectivo")
    assert resultado["ok"] is True
    print("✅ test_compra_fecha_futura_valida pasado")
