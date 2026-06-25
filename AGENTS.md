# Soporte New

FastAPI + Symfony vía Docker Compose.

## Servicios

| Servicio | Carpeta | Stack | Puerto (dev) |
|---|---|---|---|
| `app` | `app/` | Symfony 8.1 / PHP 8.4 / nginx | `8080:80` |
| `python-api` | `python-api/` | FastAPI + Paramiko | `8081:8080` |

En producción ningún servicio expone puertos al host (sin `ports:` en `docker-compose.yml`).

## Comandos

```bash
docker compose up --build                           # desarrollo (ambos servicios)
docker compose -f docker-compose.yml up --build      # producción
docker compose up --build --force-recreate           # rebuild dependencias
ruff check python-api/main.py                       # lint
mypy python-api/main.py                             # typecheck
```

## API (python-api)

Tres endpoints, todos con `?host=` query param:

| Endpoint | Descripción |
|---|---|
| `GET /home-dirs` | `ls -d1q lrn*` en `/home` vía SSH |
| `GET /host-status` | ping + port 22 check (sin SSH) |
| `GET /logged-users` | `who -u` vía SSH |

- SSH timeout 1s, `AutoAddPolicy`, credenciales de `SSH_USER` / `SSH_PASSWORD`
- Host se resuelve a IPv4 con `socket.getaddrinfo`; falla 400 si no resuelve
- Errores SSH devuelven 502
- Swagger UI solo con `DOCS_ENABLED=true` (override en dev)

## Symfony (app)

Skeleton sin controladores ni rutas personalizadas. Usa `webdevops/php-nginx:8.4` con document root en `/app/public`. En desarrollo se reemplaza por `webdevops/php-nginx-dev:8.4` con Xdebug.

## Estructura

- `python-api/main.py` — FastAPI, punto de entrada
- `python-api/Dockerfile` — Python 3.11-slim + `iputils-ping`
- `python-api/pyproject.toml` — config de ruff y mypy
- `python-api/requirements.txt` — fastapi, uvicorn, paramiko, python-dotenv, ruff, mypy, types-paramiko
- `python-api/.env` / `.env.local` — credenciales SSH (git-ignored el segundo)
- `app/` — Symfony 8.1 skeleton (composer, config, src/, public/)
- `app/Dockerfile` — `ARG APP_IMAGE`, solo cambia el WORKDIR
- `docker-compose.yml` — producción (sin puertos expuestos)
- `docker-compose.override.yml` — git-ignored, hot-reload + xdebug + puertos

## Variables de Entorno

`python-dotenv` carga `.env` luego `.env.local` con `override=True` en `main.py:9-10`. No usar `env_file` en compose.

## Notas

- Lint: `ruff check python-api/main.py` — config en `pyproject.toml`
- Typecheck: `mypy python-api/main.py` — stubs via `types-paramiko`
- No hay tests configurados (ni PHPUnit ni pytest)
- `os.environ[]` sin default — `KeyError` si faltan credenciales SSH
- `.env` / `.env.local` van dentro de `python-api/` (mapeado a `/app/` en contenedor)
- `app/.env` tiene `APP_ENV=dev` y `APP_SECRET=` vacío; `app/.env.dev` tiene el override con secret real
- `app/Dockerfile` acepta `APP_IMAGE` como build arg (útil para cambiar entre dev/prod images)
- La app corre como root en ambos contenedores
