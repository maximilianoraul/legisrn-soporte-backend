# Soporte New

Herramienta FastAPI + Paramiko para consultas SSH a servidores remotos vía Docker.

## Inicio Rápido

```bash
docker compose up --build
```

App en `http://localhost:8080`. Swagger UI solo disponible en desarrollo (`DOCS_ENABLED=true` en override).

## Estructura

- `python-api/main.py` — app FastAPI, punto de entrada
- `python-api/Dockerfile` — Python 3.11-slim + uvicorn
- `docker-compose.yml` — base (producción)
- `docker-compose.override.yml` — desarrollo (hot-reload + volume mount). Git-ignored.

## Carga de Variables de Entorno

`.env` tiene valores por defecto (commiteado). `.env.local` sobreescribe con secretos reales (git-ignored).

`python-dotenv` carga ambos en `main.py`: `.env` primero, luego `.env.local` con `override=True`.

No usar `env_file` en docker-compose para esto — Python lo maneja directamente.

## Comandos

```bash
# Desarrollo (hot-reload)
docker compose up --build

# Producción (sin hot-reload)
docker compose -f docker-compose.yml up --build

# Rebuild después de cambiar dependencias
docker compose up --build --force-recreate
```

## Notas

- `docker-compose.override.yml` está git-ignored — contiene puertos, volumes, comando de reload
- `.env.local` está git-ignored — contiene credenciales SSH reales
- Credenciales SSH se cargan vía `os.environ[]` — lanza `KeyError` si faltan las variables
- La app corre como root en el contenedor (sin usuario non-root configurado)
- No hay tests, lint ni typecheck configurados
