# Salud Vital - VitalApp AlzateAndica-Aranzazu-Carbajal

"Primera ejecución del pipeline."

## Descripción

VitalApp es una aplicación web desarrollada para la clínica Salud Vital que permite a los pacientes:
- Agendar citas médicas
- Consultar resultados médicos
- Recibir alertas de salud personalizadas

## Arquitectura del Sistema

La aplicación está construida con las siguientes tecnologías:
- **FastAPI**: Framework para la creación de la API REST
- **Python**: Lenguaje de programación principal
- **Docker**: Contenedorización de la aplicación
- **GitHub Actions**: Pipeline CI/CD
- **Pytest**: Framework de pruebas unitarias

## Estructura del Proyecto

```
├── app/                 # Código fuente de la aplicación
│   ├── main.py          # Punto de entrada de la API
│   ├── cita_manager.py  # Gestión de citas médicas
│   ├── historial_cita.py # Historial de citas y diagnósticos
│   ├── resultados.py     # Gestión de resultados médicos
│   └── alertas.py       # Sistema de alertas de salud
├── tests/               # Pruebas unitarias
├── documentation/       # Documentación del proyecto
├── Dockerfile           # Definición de la imagen Docker
├── docker-compose.yml   # Configuración de Docker Compose
└── requirements.txt     # Dependencias del proyecto
```

## Variables de Entorno

La aplicación soporta la siguiente variable de entorno:
- `frontDesplegado`: URL del frontend que consume la API (por defecto "*")

## Pipeline CI/CD

El proyecto implementa un pipeline CI/CD utilizando GitHub Actions con las siguientes etapas:
1. **Test**: Ejecución de pruebas unitarias
2. **Docker**: Construcción y publicación de la imagen Docker
3. **Deploy**: Despliegue automático de la aplicación

## Despliegue Local

Para desplegar la aplicación localmente:

```bash
docker-compose up -d
```

La aplicación estará disponible en `http://localhost:10000`

## Despliegue en AWS

La aplicación también puede desplegarse en una instancia EC2 de AWS. El pipeline CI/CD está configurado para realizar el despliegue automático en AWS después de pasar las pruebas y construir la imagen Docker.

Para habilitar el despliegue en AWS, se deben configurar los siguientes secrets en GitHub:
- `AWS_ACCESS_KEY_ID`: Clave de acceso de AWS
- `AWS_SECRET_ACCESS_KEY`: Clave secreta de AWS
- `AWS_REGION`: Región de AWS
- `AWS_EC2_INSTANCE_IP`: IP de la instancia EC2
- `SSH_PRIVATE_KEY`: Clave privada para acceder a la instancia

## Documentación

En el directorio [documentation](documentation/) se encuentran los diagramas de flujo que explican:
1. Integración de componentes durante la ejecución
2. Proceso de ejecución de pruebas
3. Consumo de la API por parte del frontend

También se incluye documentación detallada sobre:
- [Implementación del pipeline CI/CD](documentation/pipeline_implementation.md)
- [Despliegue en AWS](documentation/despliegue_aws.md)
- [Variables de entorno](documentation/variables_entorno.md)
- [Consumo de la API](documentation/consumo_api.md)