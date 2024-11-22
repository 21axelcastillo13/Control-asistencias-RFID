
  const tipoReporte = document.getElementById("tipo_reporte");
  const frecuencia = document.getElementById("frecuencia");
  const idDocente = document.getElementById("id_docente");
  const fechaInicio = document.getElementById("fecha_inicio");
  const fechaFin = document.getElementById("fecha_fin");

  // Función para actualizar el formulario basado en el tipo de reporte
  function updateForm() {
    const tipo = tipoReporte.value;
    const rango = frecuencia.value;

    if (tipo === "individual") {
      idDocente.closest(".mb-3").style.display = "block";
    } else {
      idDocente.closest(".mb-3").style.display = "none";
    }

    if (rango === "diario") {
      fechaInicio.closest(".mb-3").style.display = "block";
      fechaFin.closest(".mb-3").style.display = "none";
    } else {
      fechaInicio.closest(".mb-3").style.display = "block";
      fechaFin.closest(".mb-3").style.display = "block";
    }
  }

  tipoReporte.addEventListener("change", updateForm);
  frecuencia.addEventListener("change", updateForm);

document.addEventListener("DOMContentLoaded", () => {
  updateForm();
});

const form = document.getElementById('reporteForm');
const modal = document.getElementById('pdfModal');
const closeModal = document.getElementById('closeModal');
const pdfMessageElement = document.getElementById('pdfMessage');
const pdfFilenameElement = document.getElementById('pdfFilename');
const pdfLinkElement = document.getElementById('pdfLink');

form.addEventListener('submit', async function (e) {
  e.preventDefault(); // Previene el comportamiento por defecto del formulario

  const formData = new FormData(form);

  // Realiza la solicitud sin 'try...catch'
  const response = await fetch('/procesar', {
      method: 'POST',
      body: formData
  });

  if (!response.ok) {
      alert(`Error HTTP: ${response.status}`);
      return;
  }

  const data = await response.json();
  const errorMessageElement = document.getElementById('errorMessage');

    if (data.NoAsistencias) {
      errorMessageElement.style='block';
      errorMessageElement.textContent=data.NoAsistencias;
    }else{
      errorMessageElement.style.display='none';
    }
  
  if (data.status === "success") {
      const fileUrl = `${window.location.origin}/${data.pdf_ruta}/${data.pdf_filename}`;

      // Actualizar contenido del modal
      pdfMessageElement.textContent = data.pdf_message;
      pdfFilenameElement.textContent = data.pdf_filename;
      pdfLinkElement.href = fileUrl;

      modal.style.display = 'flex';

      form.reset();
      tipoReporte.value = "general";
      frecuencia.value = "diario";
      updateForm();
  }
});


// Cerrar modal al hacer clic en la "x"
closeModal.addEventListener('click', function () {
    modal.style.display = 'none';
});

// Cerrar modal al hacer clic fuera del contenido del modal
window.addEventListener('click', function (event) {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
