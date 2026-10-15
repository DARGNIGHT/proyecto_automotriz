async function guardarCliente() {
    const nombre = document.getElementById('c_nombre').value.trim();
    const doc = document.getElementById('c_doc').value.trim();
    const tel = document.getElementById('c_tel').value.trim();
    const email = document.getElementById('c_email').value.trim();

    if (!nombre || !doc || !tel) {
        alert("Por favor completa los campos obligatorios: Nombre, Documento y Teléfono.");
        return;
    }

    const body = {
        nombre: nombre,
        documento: doc,
        telefono: tel,
        email: email || null
    };

    try {
        const res = await fetch('/clientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("CLIENTE VINCULADO // ID: " + data.id);
            document.getElementById('v_cliente_id').value = data.id;
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function guardarVehiculo() {
    const placa = document.getElementById('v_placa').value.trim().toUpperCase();
    const marca = document.getElementById('v_marca').value.trim();
    const modelo = document.getElementById('v_modelo').value.trim();
    const anio = parseInt(document.getElementById('v_anio').value);
    const cliente_id = parseInt(document.getElementById('v_cliente_id').value);

    if (!placa || !marca || !modelo || isNaN(anio) || isNaN(cliente_id)) {
        alert("Por favor completa todos los campos del vehículo y un ID de cliente válido.");
        return;
    }

    const body = { placa, marca, modelo, anio, cliente_id };

    try {
        const res = await fetch('/vehiculos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("UNIDAD REGISTRADA // ID: " + data.id);
            document.getElementById('o_vehiculo_id').value = data.id;
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function guardarOrden() {
    const vehiculo_id = parseInt(document.getElementById('o_vehiculo_id').value);
    const diag = document.getElementById('o_diag').value.trim();
    const costo = parseFloat(document.getElementById('o_costo').value || 0);

    if (isNaN(vehiculo_id) || !diag) {
        alert("Debes indicar el ID del vehículo y un diagnóstico.");
        return;
    }

    const body = { vehiculo_id, diagnostico: diag, costo_total: costo };

    try {
        const res = await fetch('/ordenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("TICKET DIGITAL EMITIDO CORRECTAMENTE");
            cargarOrdenes();
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function cargarOrdenes() {
    try {
        const res = await fetch('/ordenes');
        if (!res.ok) return;
        const ordenes = await res.json();
        const tbody = document.getElementById('tabla_ordenes');
        tbody.innerHTML = '';
        ordenes.forEach(function(o) {
            const tr = document.createElement('tr');
            tr.innerHTML = 
                '<td><strong>#TK-' + String(o.id).padStart(4, '0') + '</strong></td>' +
                '<td>UNIDAD-' + o.vehiculo_id + '</td>' +
                '<td>' + o.diagnostico + '</td>' +
                '<td><span class="status-badge">' + o.estado + '</span></td>' +
                '<td>$' + parseFloat(o.costo_total).toLocaleString() + '</td>' +
                '<td>' + new Date(o.fecha_creacion).toLocaleDateString() + '</td>';
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error al cargar ordenes:", err);
    }
}

=======
async function guardarCliente() {
    const nombre = document.getElementById('c_nombre').value.trim();
    const doc = document.getElementById('c_doc').value.trim();
    const tel = document.getElementById('c_tel').value.trim();
    const email = document.getElementById('c_email').value.trim();

    if (!nombre || !doc || !tel) {
        alert("Por favor completa los campos obligatorios: Nombre, Documento y Teléfono.");
        return;
    }

    const body = {
        nombre: nombre,
        documento: doc,
        telefono: tel,
        email: email || null
    };

    try {
        const res = await fetch('/clientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("CLIENTE VINCULADO // ID: " + data.id);
            document.getElementById('v_cliente_id').value = data.id;
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function guardarVehiculo() {
    const placa = document.getElementById('v_placa').value.trim().toUpperCase();
    const marca = document.getElementById('v_marca').value.trim();
    const modelo = document.getElementById('v_modelo').value.trim();
    const anio = parseInt(document.getElementById('v_anio').value);
    const cliente_id = parseInt(document.getElementById('v_cliente_id').value);

    if (!placa || !marca || !modelo || isNaN(anio) || isNaN(cliente_id)) {
        alert("Por favor completa todos los campos del vehículo y un ID de cliente válido.");
        return;
    }

    const body = { placa, marca, modelo, anio, cliente_id };

    try {
        const res = await fetch('/vehiculos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("UNIDAD REGISTRADA // ID: " + data.id);
            document.getElementById('o_vehiculo_id').value = data.id;
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function guardarOrden() {
    const vehiculo_id = parseInt(document.getElementById('o_vehiculo_id').value);
    const diag = document.getElementById('o_diag').value.trim();
    const costo = parseFloat(document.getElementById('o_costo').value || 0);

    if (isNaN(vehiculo_id) || !diag) {
        alert("Debes indicar el ID del vehículo y un diagnóstico.");
        return;
    }

    const body = { vehiculo_id, diagnostico: diag, costo_total: costo };

    try {
        const res = await fetch('/ordenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (res.ok) {
            alert("TICKET DIGITAL EMITIDO CORRECTAMENTE");
            cargarOrdenes();
        } else {
            alert("ERROR: " + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert("No se pudo conectar con el servidor.");
    }
}

async function cargarOrdenes() {
    try {
        const res = await fetch('/ordenes');
        if (!res.ok) return;
        const ordenes = await res.json();
        const tbody = document.getElementById('tabla_ordenes');
        tbody.innerHTML = '';
        ordenes.forEach(function(o) {
            const tr = document.createElement('tr');
            tr.innerHTML = 
                '<td><strong>#TK-' + String(o.id).padStart(4, '0') + '</strong></td>' +
                '<td>UNIDAD-' + o.vehiculo_id + '</td>' +
                '<td>' + o.diagnostico + '</td>' +
                '<td><span class="status-badge">' + o.estado + '</span></td>' +
                '<td>$' + parseFloat(o.costo_total).toLocaleString() + '</td>' +
                '<td>' + new Date(o.fecha_creacion).toLocaleDateString() + '</td>';
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error al cargar ordenes:", err);
    }
}

>>>>>>> be3331f48e28d95f66a3b7a6bfdd7498a5a201ae
window.addEventListener('DOMContentLoaded', cargarOrdenes);