import ipaddress
import os
import socket
import subprocess

import paramiko
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(".env")
load_dotenv(".env.local", override=True)

docs_enabled = os.environ.get("DOCS_ENABLED", "false").lower() == "true"

app = FastAPI(docs_url="/docs" if docs_enabled else None, redoc_url=None)


def resolve_host(host: str) -> str:
    try:
        ip = ipaddress.IPv4Address(host)
        return str(ip)
    except ValueError:
        pass

    try:
        result = socket.getaddrinfo(host, None, socket.AF_INET)
        return str(result[0][4][0])
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"No se pudo resolver el host: {host}")


def ssh_connect(host: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        username=os.environ["SSH_USER"],
        password=os.environ["SSH_PASSWORD"],
        timeout=1
    )
    return client


@app.get("/home-dirs")
def get_home_dirs(host: str):
    ip = resolve_host(host)
    ssh = None

    try:
        ssh = ssh_connect(ip)
        stdin, stdout, stderr = ssh.exec_command(
            "cd /home && ls -d1q lrn*"
        )
        dirs = stdout.read().decode().split()
    except (paramiko.SSHException, OSError) as e:
        raise HTTPException(status_code=502, detail=f"Error de conexión SSH: {e}")
    finally:
        if ssh:
            ssh.close()

    return {"directories": dirs}


@app.get("/host-status")
def get_host_status(host: str):
    ip = resolve_host(host)

    ping = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    port_open = sock.connect_ex((ip, 22)) == 0
    sock.close()

    return {
        "ping": ping.returncode == 0,
        "ssh": port_open
    }


@app.get("/logged-users")
def get_logged_users(host: str):
    ip = resolve_host(host)
    ssh = None

    try:
        ssh = ssh_connect(ip)
        stdin, stdout, stderr = ssh.exec_command(
            "who -u"
        )

        sessions = []
        for line in stdout.read().decode().splitlines():
            parts = line.split()
            if len(parts) >= 4:
                sessions.append({
                    "user": parts[0],
                    "tty": parts[1],
                    "since": parts[2],
                    "online": parts[3]
                })
    except (paramiko.SSHException, OSError) as e:
        raise HTTPException(status_code=502, detail=f"Error de conexión SSH: {e}")
    finally:
        if ssh:
            ssh.close()

    return {"sessions": sessions}
