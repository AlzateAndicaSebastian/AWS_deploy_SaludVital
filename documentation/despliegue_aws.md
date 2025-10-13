# Despliegue en Instancia AWS

## Proceso de despliegue automático

Después de que las pruebas unitarias pasen exitosamente en el pipeline CI/CD, la aplicación se despliega automáticamente en una instancia de AWS. Este proceso se realiza en la etapa "deploy" del workflow de GitHub Actions.

## Configuración previa en la instancia AWS

### 1. Requisitos en la instancia AWS

Antes de desplegar, asegúrate de que la instancia AWS tenga instalado:

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
sudo apt install docker.io -y

# Instalar Docker Compose
sudo apt install docker-compose -y

# Iniciar y habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar el usuario al grupo docker
sudo usermod -aG docker ubuntu
```

### 2. Configuración del repositorio en la instancia

La instancia AWS debe tener el repositorio clonado y configurado:

```bash
# Clonar el repositorio
# Repositorio actualizado
 git clone https://github.com/AlzateAndicaSebastian/AWS_deploy_SaludVital.git

# Navegar al directorio del proyecto
cd AWS_deploy_SaludVital

# Configurar las credenciales de Docker Hub (si es necesario)
echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin
```

## Despliegue automático mediante GitHub Actions

El pipeline CI/CD actual ya está configurado para desplegar la aplicación. El proceso es el siguiente:

1. **Test**: Ejecución de pruebas unitarias
2. **Docker**: Construcción y publicación de la imagen Docker en Docker Hub
3. **Deploy**: Despliegue automático en la instancia AWS

### Configuración del despliegue en AWS

Para habilitar el despliegue en AWS, se necesita configurar lo siguiente en el workflow:

1. **Secrets en GitHub**:
   - `AWS_ACCESS_KEY_ID`: Clave de acceso de AWS
   - `AWS_SECRET_ACCESS_KEY`: Clave secreta de AWS
   - `AWS_REGION`: Región de AWS (ej. us-east-1)
   - `AWS_EC2_INSTANCE_IP`: IP de la instancia EC2
   - `SSH_PRIVATE_KEY`: Clave privada para acceder a la instancia
   - `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`: Credenciales de Docker Hub

2. **Actualización del workflow CI/CD**:
   El job `deploy-aws` realiza el despliegue automático usando SSH y Docker Compose:

```yaml
deploy-aws:
  needs: docker
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to AWS EC2
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.AWS_EC2_INSTANCE_IP }}
        username: ubuntu
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd AWS_deploy_SaludVital
          git pull origin main
          docker-compose down
          docker-compose pull
          docker-compose up -d
```

## Configuración de variables de entorno en AWS

Para configurar la variable `frontDesplegado` en la instancia AWS, puedes:

1. **Crear un archivo `.env` en la instancia**:
   ```bash
   echo "frontDesplegado=https://tu-front-end-desplegado.com" > .env
   ```

2. **O configurarla directamente en el docker-compose.yml**:
   ```yaml
   environment:
     - frontDesplegado=https://tu-front-end-desplegado.com
   ```

## Verificación del despliegue

Después del despliegue, puedes verificar que la aplicación esté funcionando correctamente:

```bash
# Verificar que los contenedores estén corriendo
cd AWS_deploy_SaludVital

docker-compose ps

# Verificar los logs de la aplicación
docker-compose logs

# Probar la API
curl http://localhost:10000/
```

## Acceso a la aplicación

Una vez desplegada, la aplicación estará disponible en:
- **URL**: `http://[AWS_EC2_INSTANCE_IP]:10000`
- **Puerto**: 10000 (configurado en el docker-compose.yml)

Ejemplo para tu instancia actual:
- **URL**: `http://18.215.183.193:10000/`

## Consideraciones de seguridad

1. **Firewall**: Asegúrate de que el puerto 10000 esté abierto en el grupo de seguridad de la instancia EC2
2. **HTTPS**: Para producción, considera usar un balanceador de carga con certificado SSL
3. **Variables de entorno**: Nunca expongas secretos en el código fuente