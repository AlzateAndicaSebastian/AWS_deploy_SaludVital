# Salud Vital - VitalApp AlzateAndica-Aranzazu-Carvajal

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
- `SSH_PRIVATE_KEY`: Clave privada para acceder a la instancia, esta en el repo local

## Despliegue en EC2 con Docker Compose y .env

1. Copiar el repositorio:
```bash
ssh ec2-user@IP_EC2
sudo yum install -y git docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
exit
ssh ec2-user@IP_EC2
git clone https://github.com/tu-org/tu-repo.git
cd tu-repo
```
2. Crear archivo `.env` (NO subirlo al repo):
```bash
cat > .env <<'EOF'
frontDesplegado=https://frontend.example.com
ADMIN_USERNAME=admin
ADMIN_SECRET_KEY=ClaveMuySeguraCambiar123!
EOF
```
3. Construir y levantar contenedor:
```bash
docker compose build
docker compose up -d
```
4. Verificar:
```bash
curl -s http://localhost:10000/ | jq
```
5. Rotar credenciales:
```bash
docker compose down
sed -i 's/ClaveMuySeguraCambiar123!/NuevaClaveUltraSegura456!/' .env
docker compose up -d --build
```

### Variables soportadas
- `frontDesplegado` o `FRONT_DESPLEGADO`: dominios permitidos en CORS.
- `ADMIN_USERNAME`, `ADMIN_SECRET_KEY`: credenciales del administrador único.
- `PORT` (si se parametriza en futuro).

### Persistencia
Los datos JSON se almacenan en el volumen `vitalapp_data` mapeado a `/root/memoryApps/saludVital` dentro del contenedor. Para respaldos:
```bash
docker run --rm -v vitalapp_data:/data -v $(pwd):/backup busybox tar czf /backup/backup_vitalapp_data.tgz /data
```

### Seguridad
- No subir `.env` ni llaves privadas.
- Cambiar la clave por defecto del admin antes del primer despliegue.
- Considerar mover `ADMIN_SECRET_KEY` a AWS SSM Parameter Store para mayor seguridad.

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
pruebas 