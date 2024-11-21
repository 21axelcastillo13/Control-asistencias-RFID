let asistencias = {{ asistencias | tojson }};  // Pasar los datos desde el backend a JavaScript

        function formatDate(dateString) {
            const date = new Date(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        }

        function formatTime(dateString) {
            const date = new Date(dateString);
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${hours}:${minutes}`;
        }

        function addRowToTable(rowData) {
            const tableBody = document.getElementById("table-body");
            const entrada = formatTime(rowData[1]);
            const salida = rowData[2] ? formatTime(rowData[2]) : "Pendiente";
            const clase = rowData[3];
            const imagen=rowData[4];

            // Buscar si la clase y entrada ya existen en la tabla
            const existingRow = Array.from(tableBody.rows).find(row => 
                row.cells[3].innerText === clase && row.cells[1].innerText === entrada
            );

            if (existingRow) {
                // Si existe la fila, actualizamos la salida
                existingRow.cells[2].innerText = salida === "Pendiente" ? salida : formatTime(rowData[2]);
            } else {
                // Si no existe, creamos una nueva fila
                const newRow = document.createElement("tr");
                newRow.innerHTML = `
                    <td>${rowData[0]}</td>
                    <td>${entrada}</td>
                    <td>${salida}</td>
                    <td>${clase}</td>
                    <td>${imagen}</td>
                `;
                tableBody.appendChild(newRow);  // Agregar la nueva fila
            }
        }

        function fetchRFIDData() {
            fetch('/rfid')
                .then(response => response.json())
                .then(data => {
                    if (data.asistencias) {
                        const newAsistencia = data.asistencias[data.asistencias.length - 1];  // Obtener el último registro
                        if (!asistencias.includes(newAsistencia)) {
                            asistencias.push(newAsistencia);  // Agregar el nuevo registro a la lista
                            addRowToTable(newAsistencia);  // Actualizar la tabla
                        }
                    }
                })
                .catch(error => {
                    console.error("Error fetching RFID data:", error);
                });
        }

        function renderInitialTable() {
            const tableBody = document.getElementById("table-body");
            asistencias.forEach(row => {
                const entrada = formatTime(row[1]);
                const salida = row[2] ? formatTime(row[2]) : "Pendiente";
                const clase = row[3];
                const imagen = row[4];
                const newRow = document.createElement("tr");
                newRow.innerHTML = `
                    <td>${row[0]}</td>
                    <td>${entrada}</td>
                    <td>${salida}</td>
                    <td>${clase}</td>
                    <td>${imagen}</td>
                `;
                tableBody.appendChild(newRow);
            });
        }

        // Function to update the label with the current date
        function updateDateLabel() {
            const dateLabel = document.getElementById("date-label");
            const currentDate = new Date();
            dateLabel.innerText = formatDate(currentDate);
        }

        window.onload = function() {
            updateDateLabel();  // Update the date label with the current date
            renderInitialTable();  // Renderizar tabla inicial
            setInterval(fetchRFIDData, 3000);  // Actualizar cada 3 segundos
        };

