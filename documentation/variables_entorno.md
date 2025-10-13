# Variables de Entorno

## Configuración de Variables de Entorno

La aplicación VitalApp soporta variables de entorno para personalizar su comportamiento. La variable principal es `frontDesplegado`, que permite especificar la URL del frontend que consume la API.

## Variable frontDesplegado

Esta variable define qué orígenes están permitidos para hacer solicitudes CORS (Cross-Origin Resource Sharing) a la API.

### Valores posibles:

1. **"*"** (valor por defecto): Permite solicitudes desde cualquier origen
2. **"http://localhost:3000"**: Permite solicitudes solo desde un frontend local en el puerto 3000
3. **"https://vitalApp-front-end.com"**: Permite solicitudes solo desde un dominio específico

### Cómo configurar la variable:

#### En Docker Compose:

En el archivo `docker-compose.yml` del proyecto `AWS_deploy_SaludVital`:

```yaml
environment:
  - frontDesplegado=https://tu-front-end.com
```

#### En un archivo .env:

Crear un archivo `.env` en la raíz del proyecto:

```
frontDesplegado=https://tu-front-end.com
```

#### Como variable de entorno del sistema:

En Linux/Mac:
```bash
export frontDesplegado=https://tu-front-end.com
```

En Windows:
```cmd
set frontDesplegado=https://tu-front-end.com
```

## Importancia de CORS

La configuración de CORS es fundamental para la seguridad de la aplicación. Permite controlar qué sitios web pueden interactuar con la API, previniendo ataques de tipo Cross-Site Request Forgery (CSRF).

Cuando se despliega la aplicación en producción, se recomienda establecer un valor específico para `frontDesplegado` en lugar de usar "*" para mayor seguridad.

## Ejemplo de configuración recomendada para producción

```yaml
environment:
  - frontDesplegado=https://vitalApp-front-end.com
```

## Relación con el pipeline CI/CD

El pipeline CI/CD utiliza esta variable para configurar CORS en el despliegue automático en AWS. Asegúrate de definirla correctamente en el archivo `.env` o en el `docker-compose.yml` antes de desplegar.
