const cantidadInput = document.querySelector('input[name="cantidad"]');
const edadesContainer = document.getElementById("edades-container");
const errorCantidad = document.getElementById("error-cantidad");
const fechaInput = document.querySelector('input[name="fecha_visita"]');
const errorFecha = document.getElementById("error-fecha");
const btnComprar = document.querySelector('button[type="submit"]');
const precioTotalDiv = document.getElementById("precio-total");

// --- Precios base ---
const precios = {
  regular: 5000,
  VIP: 10000
};

// --- Lista de días festivos (YYYY-MM-DD) ---
const diasFestivos = [
  "2025-01-01", "2025-03-24", "2025-04-02", "2025-05-01",
  "2025-05-25", "2025-06-17", "2025-06-20", "2025-07-09", "2025-08-17", "2025-10-12", "2025-11-20", "2025-12-08",
  "2025-12-25"
];

// --- Función para calcular descuento según edad ---
function obtenerDescuentoPorEdad(edad) {
  if (edad >= 0 && edad < 3) return 1.0;    // 100%
  if (edad >= 3 && edad < 15) return 0.5;   // 50%
  if (edad >= 15 && edad < 60) return 0.0;  // 0%
  if (edad >= 60 && edad <= 110) return 0.5;// 50%
  return 0.0;
}

// --- Calcular total dinámicamente ---
function actualizarPrecioTotal() {
  const visitantes = edadesContainer.querySelectorAll(".visitante-group");
  let total = 0;

  visitantes.forEach(v => {
    const edadInput = v.querySelector("input[type='number']");
    const paseSelect = v.querySelector("select");
    const edad = parseInt(edadInput.value);
    const tipoPase = paseSelect.value;
    const precioBase = precios[tipoPase] || 0;

    if (!isNaN(edad) && edad >= 0 && edad <= 110) {
      const descuento = obtenerDescuentoPorEdad(edad);
      total += precioBase * (1 - descuento);
    }
  });

  precioTotalDiv.textContent = `💰 Total a pagar: $${total.toFixed(2)}`;
}

// --- Obtener fecha hoy en formato YYYY-MM-DD ---
function obtenerFechaHoy() {
  const hoy = new Date();
  const yyyy = hoy.getFullYear();
  const mm = String(hoy.getMonth() + 1).padStart(2, '0');
  const dd = String(hoy.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

// --- Validar fecha ---
fechaInput.addEventListener("input", () => {
  const valor = fechaInput.value;
  const fechaSeleccionada = new Date(valor);
  const hoy = new Date(obtenerFechaHoy());
  const limite = new Date(hoy);
  limite.setMonth(limite.getMonth() + 1); // máximo un mes

  const diaSemana = fechaSeleccionada.getDay(); // 0 = lunes

  errorFecha.textContent = "";
  btnComprar.disabled = false;

  if (isNaN(fechaSeleccionada.getTime())) {
    errorFecha.textContent = "⚠️ Debes seleccionar una fecha válida.";
    btnComprar.disabled = true;
    return;
  }

  // Validaciones
  if (fechaSeleccionada < hoy) {
    errorFecha.textContent = "⚠️ La fecha no puede ser anterior a hoy.";
    btnComprar.disabled = true;
  } else if (fechaSeleccionada > limite) {
    errorFecha.textContent = "⚠️ Solo se pueden reservar entradas hasta 1 mes antes.";
    btnComprar.disabled = true;
  } else if (diaSemana === 0) { // lunes cerrado
    errorFecha.textContent = "🚫 El parque está cerrado los lunes.";
    btnComprar.disabled = true;
  } else if (diasFestivos.includes(valor)) {
    errorFecha.textContent = "🚫 El parque está cerrado en días festivos.";
    btnComprar.disabled = true;
  } else {
    errorFecha.textContent = "";
    btnComprar.disabled = false;
  }
});

// --- Generar campos de visitantes dinámicamente ---
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
    group.className = "visitante-group";

    // Edad
    const labelEdad = document.createElement("label");
    labelEdad.textContent = `Edad visitante ${i + 1}: `;

    const inputEdad = document.createElement("input");
    inputEdad.type = "number";
    inputEdad.name = `edad_${i}`;
    inputEdad.min = 0;
    inputEdad.max = 110;
    inputEdad.required = true;

    const errorSpan = document.createElement("span");
    errorSpan.className = "edad-error";

    // Tipo de pase
    const labelPase = document.createElement("label");
    labelPase.textContent = "Tipo de pase: ";

    const selectPase = document.createElement("select");
    selectPase.name = `pase_${i}`;
    selectPase.innerHTML = `
      <option value="regular">Regular</option>
      <option value="VIP">VIP</option>
    `;

    // Listeners
    inputEdad.addEventListener("input", () => {
      const valor = parseInt(inputEdad.value);
      if (isNaN(valor) || valor < 0) {
        inputEdad.classList.add("input-error");
        errorSpan.textContent = "⚠️ Edad inválida";
      } else if (valor > 110) {
        inputEdad.classList.add("input-error");
        errorSpan.textContent = "⚠️ La edad no puede superar los 110 años";
      } else {
        inputEdad.classList.remove("input-error");
        errorSpan.textContent = "";
      }
      actualizarPrecioTotal();
    });

    selectPase.addEventListener("change", actualizarPrecioTotal);

    group.appendChild(labelEdad);
    group.appendChild(inputEdad);
    group.appendChild(errorSpan);
    group.appendChild(labelPase);
    group.appendChild(selectPase);

    edadesContainer.appendChild(group);
  }

  actualizarPrecioTotal();
});

// --- Enviar formulario ---
document.getElementById("form-compra").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const email = "miligaliano@gmail.com";
  const fecha_visita = form.fecha_visita.value;
  const cantidad = parseInt(form.cantidad.value);
  const forma_pago = form.forma_pago.value;

  const visitantes = edadesContainer.querySelectorAll(".visitante-group");
  const edades = [];
  const tipos_pase = [];

  for (let v of visitantes) {
    const edad = parseInt(v.querySelector("input").value);
    const pase = v.querySelector("select").value;
    if (isNaN(edad) || edad < 0 || edad > 110) {
      document.getElementById("resultado").innerHTML = `<strong>⚠️ Las edades deben estar entre 0 y 110.</strong>`;
      return;
    }
    edades.push(edad);
    tipos_pase.push(pase);
  }

  const payload = {
    email,
    fecha_visita,
    cantidad,
    edades,
    tipo_pase: tipos_pase,
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

      fetch("http://localhost:8000/enviar-confirmacion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, mensaje: data.mensaje })
      })
        .then(res => res.json())
        .then(data => {
          if (data.ok) console.log("📩 Correo enviado correctamente");
          else console.error("❌ Error al enviar el correo:", data.detail);
        })
        .catch(err => console.error("❌ Error de conexión al enviar el correo:", err));

    } else {
      resultado.innerHTML = `<strong>⚠️ ${data.detail}</strong>`;
    }
  } catch (err) {
    document.getElementById("resultado").innerHTML = `<strong>❌ Error de conexión con el servidor.</strong>`;
  }
});
