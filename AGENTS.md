# Soporte New

FastAPI + Paramiko SSH consultas vía Docker.

## Comandos

```bash
docker compose up --build                          # desarrollo (hot-reload)
docker compose -f docker-compose.yml up --build     # producción
docker compose up --build --force-recreate          # rebuild dependencias
ruff check python-api/main.py                      # lint
mypy python-api/main.py                            # typecheck
```

App en `http://localhost:8080`. Swagger UI solo con `DOCS_ENABLED=true` (override).

## API

Tres endpoints, todos con `?host=` como query param:

| Endpoint | Descripción |
|---|---|
| `GET /home-dirs` | `ls -d1q lrn*` en `/home` vía SSH |
| `GET /host-status` | ping + port 22 check (sin SSH) |
| `GET /logged-users` | `who -u` vía SSH |

- SSH timeout 1s, `AutoAddPolicy`, credenciales de env vars `SSH_USER` / `SSH_PASSWORD`
- Host se resuelve a IPv4 con `socket.getaddrinfo`; falla con 400 si no resuelve
- Errores SSH devuelven 502

## Estructura

- `python-api/main.py` — app FastAPI, punto de entrada
- `python-api/Dockerfile` — Python 3.11-slim + `iputils-ping` (para `/host-status`)
- `python-api/.env` — defaults commiteados; `.env.local` (git-ignored) sobreescribe
- `python-api/requirements.txt` — fastapi, uvicorn, paramiko, python-dotenv, ruff, mypy
- `python-api/pyproject.toml` — config de ruff y mypy
- `docker-compose.yml` — base (producción, 3 líneas)
- `docker-compose.override.yml` — git-ignored, hot-reload + volume + `DOCS_ENABLED=true`

## Variables de Entorno

`python-dotenv` carga `.env` luego `.env.local` con `override=True` en `main.py:9-10`. No usar `env_file` en compose.

## Notas

- Lint: `ruff check python-api/main.py` — config en `pyproject.toml`
- Typecheck: `mypy python-api/main.py` — stubs via `types-paramiko`
- No hay tests configurados
- La app corre como root en el contenedor
- `os.environ[]` sin default — `KeyError` si faltan credenciales
- `.env` y `.env.local` van dentro de `python-api/` (host path mapeado a `/app/` en contenedor)
