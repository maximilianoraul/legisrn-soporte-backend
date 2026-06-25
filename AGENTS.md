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

Usa `webdevops/php-nginx:8.4` con document root en `/app/public`. En desarrollo se reemplaza por `webdevops/php-nginx-dev:8.4` con Xdebug.

### Página `/`

Formulario con input de IP/DNS + botón Consultar. SPA via Stimulus + AssetMapper.

Flujo:

`Stimulus → GET /api/host-status?host=X → PythonApiService → python-api:8080`

Si ping+SSH OK, el frontend lanza en paralelo:

`Stimulus → GET /api/home-dirs?host=X → PythonApiService → python-api:8080`
`Stimulus → GET /api/logged-users?host=X → PythonApiService → python-api:8080`

Cada sección muestra su propio indicador de carga mientras se resuelve la request.

### Endpoints internos (proxy a Python API)

| Endpoint | Descripción |
|---|---|
| `GET /api/host-status?host=X` | Proxy a `/host-status` |
| `GET /api/home-dirs?host=X` | Proxy a `/home-dirs` |
| `GET /api/logged-users?host=X` | Proxy a `/logged-users` |

### Paquetes agregados

`symfony/asset-mapper`, `symfony/stimulus-bundle`, `symfony/http-client`, `symfony/twig-bundle` — todos `8.1.*` excepto stimulus-bundle (`^3.2`).

## Estructura

- `python-api/main.py` — FastAPI, punto de entrada
- `python-api/Dockerfile` — Python 3.11-slim + `iputils-ping`
- `python-api/pyproject.toml` — config de ruff y mypy
- `python-api/requirements.txt` — fastapi, uvicorn, paramiko, python-dotenv, ruff, mypy, types-paramiko
- `python-api/.env` / `.env.local` — credenciales SSH (git-ignored el segundo)
- `app/` — Symfony 8.1 (composer, config, src/, public/)
- `app/src/Controller/HostCheckController.php` — página `/` + proxy `/api/host-status`, `/api/home-dirs`, `/api/logged-users`
- `app/src/Service/PythonApiService.php` — wrapper que consulta python-api
- `app/templates/host_check/index.html.twig` — formulario con Stimulus
- `app/assets/controllers/host_check_controller.js` — Stimulus controller SPA
- `app/assets/app.js` — entrypoint JS (importmap)
- `app/importmap.php` — mapeo de módulos JS (`@hotwired/stimulus`, `app`)
- `app/Dockerfile` — `ARG APP_IMAGE`, solo cambia el WORKDIR
- `docker-compose.yml` — producción (sin puertos expuestos) + env vars `NO_PROXY`, `no_proxy`
- `docker-compose.override.yml` — git-ignored, hot-reload + xdebug + puertos

## Variables de Entorno

### Python API

`python-dotenv` carga `.env` luego `.env.local` con `override=True` en `main.py:9-10`. No usar `env_file` en compose.

### Symfony (`docker-compose.yml`)

- `PYTHON_API_URL=http://python-api:8080` — base URL para `PythonApiService` (definido en `config/services.yaml`)
- `NO_PROXY` / `no_proxy` — si el host tiene proxy configurado, ambas variantes deben incluir `python-api` para que la llamada interna no pase por el proxy

## Notas

- Lint: `ruff check python-api/main.py` — config en `pyproject.toml`
- Typecheck: `mypy python-api/main.py` — stubs via `types-paramiko`
- No hay tests configurados (ni PHPUnit ni pytest)
- `os.environ[]` sin default — `KeyError` si faltan credenciales SSH
- `.env` / `.env.local` van dentro de `python-api/` (mapeado a `/app/` en contenedor)
- `app/.env` tiene `APP_ENV=dev` y `APP_SECRET=` vacío; `app/.env.dev` tiene el override con secret real
- `app/Dockerfile` acepta `APP_IMAGE` como build arg (útil para cambiar entre dev/prod images)
- La app corre como root en ambos contenedores
