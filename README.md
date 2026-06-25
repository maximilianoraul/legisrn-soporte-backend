# Soporte New

FastAPI + Symfony vía Docker Compose.

## Requisitos

- Docker
- Docker Compose

## Servicios

| Servicio | Carpeta | Stack | Dev URL |
|---|---|---|---|
| Symfony app | `app/` | PHP 8.4 + nginx | `http://localhost:8080` |
| Python API | `python-api/` | FastAPI + Paramiko | `http://localhost:8081` |

La página principal en `http://localhost:8080` (`/`) tiene un formulario para consultar IP/DNS vía SSH. El flujo es SPA (Stimulus): el front consulta al backend Symfony, que usa `PythonApiService` para llamar a la Python API por el nombre interno del servicio Docker (`python-api:8080`).

## Levantar el stack

```bash
docker compose up --build
```

### Desarrollo (hot-reload + Xdebug + Swagger)

El archivo `docker-compose.override.yml` (git-ignored) se carga automáticamente y habilita:

- **Symfony**: `webdevops/php-nginx-dev:8.4` con Xdebug, puerto `8080:80`
- **Python API**: uvicorn con `--reload`, Swagger UI (`DOCS_ENABLED=true`), puerto `8081:8080`

### Producción

```bash
docker compose -f docker-compose.yml up --build
```

En producción ningún servicio expone puertos al host — requiere reverse proxy externo.

## Credenciales SSH (Python API)

Se configuran en `python-api/.env` (commiteado, defaults) y `python-api/.env.local` (git-ignored, reales):

```dotenv
SSH_USER=admin
SSH_PASSWORD=secret
```

`python-dotenv` carga `.env` primero y `.env.local` sobreescribe.

## Endpoints de la Python API

Todos requieren `?host=` como query param:

- `GET /home-dirs` — lista directorios `lrn*` en `/home` vía SSH
- `GET /host-status` — ping + puerto 22 (sin SSH)
- `GET /logged-users` — `who -u` vía SSH
