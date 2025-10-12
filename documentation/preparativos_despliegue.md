# Preparativos para el despliegue automático de VitalApp

Este documento describe los pasos y configuraciones necesarias entre el proyecto, GitHub Actions y AWS (IAM e instancias EC2) para garantizar un push y despliegue exitoso del backend.

---

## 1. Preparativos en el Proyecto

- **Estructura del proyecto:**
  - Código fuente organizado en la carpeta `app/`.
  - Pruebas unitarias en la carpeta `tests/`.
  - Archivo `requirements.txt` con dependencias de Python.
  - Archivo `Dockerfile` para construir la imagen del backend.
  - Archivo `docker-compose.yml` para orquestar el despliegue del contenedor.
  - Archivo `.env` para variables de entorno.

- **Pruebas:**
  - Implementación de pruebas con `pytest`.
  - Verificación de que las pruebas se ejecutan correctamente localmente.

---

## 2. Configuración de GitHub Actions

- **Workflow CI/CD:**
  - Archivo `.github/workflows/ci-cd.yml` con los siguientes jobs:
    - `test`: Ejecuta pruebas unitarias.
    - `docker`: Construye y publica la imagen en Docker Hub.
    - `deploy`: Despliega localmente con Docker Compose.
    - `deploy-aws`: Despliega en EC2 vía SSH.

- **Secretos en GitHub:**
  - Configuración de los siguientes secretos en el repositorio:
    - `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` (credenciales de Docker Hub).
    - `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` (credenciales IAM de AWS).
    - `AWS_REGION` (región de la instancia EC2).
    - `AWS_EC2_INSTANCE_IP` (IP pública de la instancia EC2).
    - `SSH_PRIVATE_KEY` (clave privada para acceso SSH a EC2).

---

## 3. Configuración en AWS

### IAM (Identity and Access Management)
- Creación de un usuario IAM con permisos mínimos necesarios para EC2 y ECR (si aplica).
- Generación de las claves de acceso (`AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`).

### Instancia EC2
- Lanzamiento de una instancia EC2 (Ubuntu recomendado).
- Asignación de una IP pública.
- Creación y descarga de un par de claves (key pair) para acceso SSH.
- Asociación de un Security Group con reglas:
  - Permitir tráfico entrante por el puerto 22 (SSH) desde tu IP o `0.0.0.0/0`.
  - Permitir tráfico entrante por el puerto 10000 (aplicación) desde la IP del frontend o `0.0.0.0/0`.

### Preparativos en la instancia EC2
- Acceso por SSH usando la clave privada.
- Actualización de paquetes:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- Instalación de Docker y Docker Compose:
  ```bash
  sudo apt install docker.io -y
  sudo apt install docker-compose -y
  sudo systemctl start docker && sudo systemctl enable docker
  sudo usermod -aG docker ubuntu
  ```
- Verificación de permisos y conectividad.

---

## 4. Pasos previos al push

- Verificar que el proyecto funciona localmente y pasa las pruebas.
- Confirmar que los secretos están correctamente configurados en GitHub.
- Comprobar que la instancia EC2 está activa y accesible por SSH.
- Validar que los puertos necesarios están abiertos en el Security Group.
- Realizar el push al repositorio y monitorear la ejecución del workflow en GitHub Actions.

---

## 5. Verificación final

- Acceder a la instancia EC2 y verificar que el contenedor está corriendo:
  ```bash
  docker ps
  ```
- Probar el acceso a la API desde el frontend o con herramientas como `curl`:
  ```bash
  curl http://<IP_PUBLICA_EC2>:10000/endpoint
  ```

---

**Con estos preparativos, el despliegue automático y el consumo de la API desde el frontend estarán garantizados.**

