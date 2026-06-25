# Soporte New

Herramienta FastAPI + Paramiko para consultas SSH a servidores remotos vía Docker.

## Requisitos

- Docker
- Docker Compose

## Levantar el stack

```bash
docker compose up --build
```

La app queda disponible en `http://localhost:8080`.

> En desarrollo, Swagger UI queda habilitado en `http://localhost:8080/docs`.

## Credenciales SSH

Las credenciales se configuran en archivos `.env` dentro de `python-api/`:

| Archivo                 | Propósito                     | ¿Se commitea? |
| ----------------------- | ----------------------------- | ------------- |
| `python-api/.env`       | Valores por defecto (ejemplo) | Sí            |
| `python-api/.env.local` | Credenciales reales           | No            |

### Archivo `.env` (ejemplo)

```
SSH_USER=admin
SSH_PASSWORD=secret
```

### Archivo `.env.local` (real)

```
SSH_USER=tu_usuario
SSH_PASSWORD=tu_contraseña
```

> `python-dotenv` carga `.env` primero y `.env.local` sobreescribe los valores.

## Desarrollo con hot-reload

El archivo `docker-compose.override.yml` se carga automáticamente con `docker compose up` y habilita:

- **Hot-reload**: uvicorn con `--reload`
- **Volume mount**: cambios en `python-api/` se reflejan en el contenedor
- **Swagger UI**: habilitado via `DOCS_ENABLED=true`

```yaml
services:
  app:
    build:
      args:
        APP_IMAGE: webdevops/php-nginx-dev:8.4
    environment:
      APP_ENV: dev
      PHP_DEBUGGER: xdebug
      PHP_MEMORY_LIMIT: 1024M
      XDEBUG_MODE: debug
      XDEBUG_DISCOVER_CLIENT_HOST: yes
      XDEBUG_START_WITH_REQUEST: yes
      XDEBUG_CLIENT_HOST: 172.17.0.1
      XDEBUG_CLIENT_PORT: 9003
      XDEBUG_IDE_KEY: PHPSTORM
    ports:
      - "8080:80"

  python-api:
    environment:
      - DOCS_ENABLED=true
    ports:
      - "8081:8080"
    volumes:
      - ./python-api:/app
    command:
      ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```

> Este archivo está git-ignored para no afectar producción.

## Producción (sin hot-reload)

```bash
docker compose -f docker-compose.yml up --build
```

> En producción, Swagger UI está deshabilitado.
