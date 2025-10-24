const cantidadInput = document.querySelector('input[name="cantidad"]');
const tipoPaseSelect = document.querySelector('select[name="tipo_pase"]');
const edadesContainer = document.getElementById("edades-container");
const errorCantidad = document.getElementById("error-cantidad");
const fechaInput = document.querySelector('input[name="fecha_visita"]');
const errorFecha = document.getElementById("error-fecha");
const btnComprar = document.querySelector('button[type="submit"]');
function actualizarPrecioTotal() {
  const cantidad = parseInt(cantidadInput.value);
  const tipoPase = document.querySelector('select[name="tipo_pase"]').value;
  const precioTotalDiv = document.getElementById("precio-total");

  const precios = {
    regular: 10000,
    VIP: 15000
  };

  const precioUnitario = precios[tipoPase] || 0;
  const total = !isNaN(cantidad) ? cantidad * precioUnitario : 0;

  precioTotalDiv.textContent = `💰 Total a pagar: $${total}`;
}

function obtenerFechaHoy() {
  const hoy = new Date();
  const yyyy = hoy.getFullYear();
  const mm = String(hoy.getMonth() + 1).padStart(2, '0'); // Meses van de 0 a 11
  const dd = String(hoy.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`; // Formato: "2025-10-24"
}
fechaInput.addEventListener("input", () => {
  const valor = fechaInput.value;
  const fechaSeleccionada = new Date(valor);
  const hoy = obtenerFechaHoy();

  const diaSemana = fechaSeleccionada.getDay(); // 6 = domingo

  errorFecha.textContent = ""; // Limpiar mensaje anterior

  if (isNaN(fechaSeleccionada.getTime())) {
    fechaInput.classList.add("input-error");
    errorFecha.textContent = "⚠️ Debes seleccionar una fecha válida.";
    btnComprar.disabled = true;
    return;
  }

  if (valor < hoy) {
    fechaInput.classList.add("input-error");
    errorFecha.textContent = "⚠️ La fecha no puede ser anterior a hoy.";
    btnComprar.disabled = true;
  } else if (diaSemana === 6) {
    fechaInput.classList.add("input-error");
    errorFecha.textContent = "🚫 El parque está cerrado los domingos.";
    btnComprar.disabled = true;
  } else {
    fechaInput.classList.remove("input-error");
    errorFecha.textContent = ""; // Fecha válida
    btnComprar.disabled = false;
  }
});


cantidadInput.addEventListener("input", () => {
  const cantidad = parseInt(cantidadInput.value);
  edadesContainer.innerHTML = "";
  errorCantidad.textContent = "";

  if (isNaN(cantidad)) return;

  if (cantidad > 10) {
    errorCantidad.textContent = "⚠️ No se pueden comprar más de 10 entradas.";
    return;
  }

  if (cantidad < 1) {
    errorCantidad.textContent = "⚠️ No se puede comprar menos de 1 entrada.";
    return;
  }

  for (let i = 0; i < cantidad; i++) {
    const group = document.createElement("div");
    group.className = "edad-group";

    const label = document.createElement("label");
    label.textContent = `Edad visitante ${i + 1}:`;

    const input = document.createElement("input");
    input.type = "number";
    input.name = `edad_${i}`;
    input.required = true;

    const errorSpan = document.createElement("span"); // ✅ Crear antes del listener
    errorSpan.className = "edad-error";
    errorSpan.textContent = "";

    // ✅ Validación en tiempo real
    input.addEventListener("input", () => {
      const valor = parseInt(input.value);
      if (isNaN(valor) || valor <= 0) {
        input.classList.add("input-error");
        errorSpan.textContent = "⚠️ Se debe ingresar una edad válida (mayor a 0)";
      } else {
        input.classList.remove("input-error");
        errorSpan.textContent = "";
      }
    });

    group.appendChild(label);
    group.appendChild(input);
    group.appendChild(errorSpan);
    edadesContainer.appendChild(group);
    
    actualizarPrecioTotal();
  }
});

tipoPaseSelect.addEventListener("change", actualizarPrecioTotal);


document.getElementById("form-compra").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const email = "miligaliano@gmail.com";
  const fecha_visita = form.fecha_visita.value;
  const cantidad = parseInt(form.cantidad.value);
  const tipo_pase = form.tipo_pase.value;
  const forma_pago = form.forma_pago.value;

  const edadesInputs = edadesContainer.querySelectorAll("input");
  const edades = [];

  for (let input of edadesInputs) {
    const edad = parseInt(input.value);
    if (isNaN(edad) || edad <= 0) {
      document.getElementById("resultado").innerHTML = `<strong>⚠️ Las edades deben ser números mayores a cero.</strong>`;
      return;
    }
    edades.push(edad);
  }

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
      // ✅ Enviar correo con el mensaje recibido
  fetch("http://localhost:8000/enviar-confirmacion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email, // el mismo email que usaste en /comprar
      mensaje: data.mensaje
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.ok) {
      console.log("📩 Correo enviado correctamente");
    } else {
      console.error("❌ Error al enviar el correo:", data.detail);
    }
  })
  .catch(err => {
    console.error("❌ Error de conexión al enviar el correo:", err);
  });
    } else {
      resultado.innerHTML = `<strong>⚠️ ${data.detail}</strong>`;
    }
  } catch (err) {
    document.getElementById("resultado").innerHTML = `<strong>❌ Error de conexión con el servidor.</strong>`;
  }
});
