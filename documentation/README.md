# Documentación del Proyecto Salud Vital

Este directorio contiene la documentación del proyecto Salud Vital, incluyendo diagramas de flujo, variables de entorno, consumo de la API y explicaciones sobre la arquitectura del sistema.

## Repositorio principal
- **Nombre:** AWS_deploy_SaludVital
- **URL:** https://github.com/AlzateAndicaSebastian/AWS_deploy_SaludVital

## Despliegue automático (CI/CD)
El proyecto utiliza un pipeline CI/CD en GitHub Actions que realiza:
1. Pruebas unitarias
2. Construcción y publicación de la imagen Docker en Docker Hub
3. Despliegue automático en una instancia AWS EC2 usando Docker Compose

Consulta la documentación detallada en `despliegue_aws.md`.

## Consumo de la API
La API se expone en la instancia AWS EC2 en el puerto 10000. Ejemplo de acceso:
- **URL:** http://18.215.183.193:10000/

Consulta los endpoints y ejemplos de consumo en `consumo_api.md`.

## Variables de entorno
La variable principal es `frontDesplegado`, que controla los orígenes permitidos para CORS. Consulta cómo configurarla en `variables_entorno.md`.

## Documentación adicional
- Diagramas de flujo: `flujo_consumo_web.mmd`, `flujo_integracion.mmd`, `flujo_pruebas.mmd`
- Pipeline CI/CD: `pipeline_implementation.md`
- Preparativos de despliegue: `preparativos_despliegue.md`

## Recomendaciones de seguridad
- Configura correctamente el grupo de seguridad en AWS para exponer solo los puertos necesarios.
- Usa HTTPS en producción. hay que configurarlo (pendiente).
- No expongas secretos en el código fuente.

---
Para cualquier duda sobre el despliegue, consumo o configuración, revisa los archivos de documentación específicos en este directorio.
