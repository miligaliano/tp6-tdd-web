document.getElementById("form-compra").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const email = "usuario@registrado.com";
  const fecha_visita = form.fecha_visita.value;
  const cantidad = parseInt(form.cantidad.value);
  const edades = Array(cantidad).fill(25);
  const tipo_pase = form.tipo_pase.value;
  const forma_pago = form.forma_pago.value;

  const payload = {
    email,
    fecha_visita,
    cantidad,
    edades,
    tipo_pase,
    forma_pago
  };

  try {
    const res = await fetch("http://localhost:8000/comprar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    const resultado = document.getElementById("resultado");

    if (res.ok) {
      resultado.innerHTML = `<strong>✅ ${data.mensaje}</strong>`;
    } else {
      resultado.innerHTML = `<strong>⚠️ ${data.detail}</strong>`;
    }
  } catch (err) {
    document.getElementById("resultado").innerHTML = `<strong>❌ Error de conexión con el servidor.</strong>`;
  }
});
