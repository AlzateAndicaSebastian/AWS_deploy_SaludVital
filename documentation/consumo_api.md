# Consumo de la API desde el Frontend

## Endpoints disponibles

La API de VitalApp expone los siguientes endpoints:

### 1. Estado de la aplicación
- **URL**: `http://18.215.183.193:10000/`
- **Método**: GET
- **Descripción**: Verifica que la API esté funcionando correctamente
- **Respuesta**: 
  ```json
  {
    "status": "active",
    "message": "VitalApp API is running"
  }
  ```

### 2. Agendar cita médica
- **URL**: `http://18.215.183.193:10000/citas`
- **Método**: POST
- **Descripción**: Permite agendar una nueva cita médica
- **Parámetros**:
  - `paciente` (string): Nombre del paciente
  - `medico` (string): Nombre del médico
  - `fecha` (string): Fecha de la cita (formato YYYY-MM-DD)
- **Respuesta**:
  ```json
  {
    "message": "Cita creada exitosamente"
  }
  ```

### 3. Obtener diagnóstico
- **URL**: `http://18.215.183.193:10000/diagnosticos/{paciente}/{fecha}`
- **Método**: GET
- **Descripción**: Obtiene el diagnóstico de una cita específica
- **Parámetros**:
  - `paciente` (path): Nombre del paciente
  - `fecha` (path): Fecha de la cita (formato YYYY-MM-DD)
- **Respuesta**:
  ```json
  {
    "diagnostico": "Descripción del diagnóstico"
  }
  ```

### 4. Obtener alertas
- **URL**: `http://18.215.183.193:10000/alertas/{paciente}`
- **Método**: GET
- **Descripción**: Obtiene las alertas de salud para un paciente específico
- **Parámetros**:
  - `paciente` (path): Nombre del paciente
- **Respuesta**:
  ```json
  {
    "alertas": [
      "Alerta: glucosa = 120",
      "Alerta: presion = 145"
    ]
  }
  ```

## Ejemplo de consumo desde JavaScript

```javascript
// Obtener el estado de la aplicación
fetch('http://18.215.183.193:10000/')
  .then(response => response.json())
  .then(data => console.log(data));

// Agendar una cita
fetch('http://18.215.183.193:10000/citas', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    paciente: 'Juan Pérez',
    medico: 'Dr. Smith',
    fecha: '2025-04-10'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// Obtener diagnóstico
fetch('http://18.215.183.193:10000/diagnosticos/Juan Pérez/2025-04-10')
  .then(response => response.json())
  .then(data => console.log(data));

// Obtener alertas
fetch('http://18.215.183.193:10000/alertas/Juan Pérez')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Notas
- Cambia la IP por la de tu instancia si es diferente.
- Asegúrate de que el puerto 10000 esté abierto en el grupo de seguridad de AWS.
- Puedes acceder a la documentación interactiva de la API en: `http://18.215.183.193:10000/docs`

## Consideraciones de seguridad

1. **CORS**: La API está configurada para permitir solicitudes solo desde el origen especificado en la variable de entorno `frontDesplegado`.

2. **HTTPS**: En producción, se recomienda acceder a la API a través de HTTPS para garantizar la seguridad de la comunicación.

3. **Validación de datos**: Si bien la API realiza validaciones básicas, es recomendable también validar los datos en el frontend antes de enviarlos.